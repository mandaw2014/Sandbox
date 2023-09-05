from panda3d.core import WindowProperties, FrameBufferProperties, GraphicsPipe, Texture, GraphicsOutput, SamplerState, OrthographicLens, Shader, Camera, NodePath, PandaNode, PNMImage
from ursina import Entity, camera
from math import sqrt
from random import random


class SceneLighting(Entity):
    def __init__(self, ursina, player, sun_direction = (0.75, -1, 0.5), sun_color = (1.0, 0.7, 0.3, 1.0), ambient_color = (0.6, 0.65, 0.7, 0.5), 
                 shadow_resolution = 2048, shadow_size = 100, shadow_height = 200, shadow_bias = 0.0, shadow_camera_direction_offset = True, 
                 shadow_filter_radius = 3.0, shadow_filter_samples = 10.0, soft_shadows = True,
                 sky_texture = None, sky_color = (1.0, 1.0, 1.0, 1.5), gamma = 2.0):

        self.player = player
        self.shadow_camera_direction_offset = (shadow_size / 2.0) * shadow_camera_direction_offset

        # noise texture creation for random values in shader
        def createNoiseTexture(tex_size):
            noise_img = PNMImage(tex_size, tex_size)

            for x in range(tex_size):
                for y in range(tex_size):
                    noise_img.setRed(x, y, random())

            noise_texture = Texture("noise texture")
            noise_texture.load(noise_img)
            noise_texture.setMagfilter(SamplerState.FT_nearest)
            noise_texture.setMagfilter(SamplerState.FT_nearest)
            return noise_texture


        # sky
        if (sky_texture):
            self.sky_shader = Shader.load(lang = Shader.SL_GLSL, vertex = "shaders/sky_vert.glsl", fragment = "shaders/sky_frag.glsl")
            self.sky = Entity(model = "sphere", texture = sky_texture, scale = 5000, double_sided = True, color = sky_color)
            self.sky.setShader(self.sky_shader)
            self.sky.setShaderInput("gamma", gamma)

        # bufffer creation
        win_prop = WindowProperties(size = (shadow_resolution, shadow_resolution))
        fb_prop = FrameBufferProperties()
        fb_prop.setRgbColor(1)
        fb_prop.setAlphaBits(1)
        fb_prop.setDepthBits(1)
        shadow_buffer = ursina.graphicsEngine.makeOutput(ursina.pipe, "shadow buffer", -100, fb_prop, win_prop, GraphicsPipe.BFRefuseWindow, ursina.win.getGsg(), ursina.win)

        shadow_tex = Texture()
        shadow_buffer.addRenderTexture(shadow_tex, GraphicsOutput.RTM_bind_or_copy,
                                 GraphicsOutput.RTP_depth_stencil)
        shadow_tex.setMinfilter(SamplerState.FT_nearest)
        shadow_tex.setMagfilter(SamplerState.FT_nearest)
        shadow_tex.setWrapU(Texture.WM_border_color)
        shadow_tex.setWrapV(Texture.WM_border_color)
        shadow_tex.setBorderColor((1.0, 1.0, 1.0, 1.0))

        shadow_buffer.setClearActive(GraphicsOutput.RTP_depth, True)
        shadow_buffer.setClearValue(GraphicsOutput.RTP_depth, 1.0)

        # shadow camera creation
        self.shadow_cam = Camera("shadow camera")
        shadow_cam_lens = OrthographicLens()
        shadow_cam_lens.setFilmSize(shadow_size, shadow_size)
        shadow_cam_lens.setFilmOffset(0, 0)
        shadow_cam_lens.setNearFar(-shadow_height, shadow_height)
        self.shadow_cam.setLens(shadow_cam_lens)

        self.shadow_cam_np = ursina.render.attachNewNode(self.shadow_cam)
        self.shadow_cam_np.lookAt(sun_direction)

        display_region = shadow_buffer.makeDisplayRegion()
        display_region.disableClears()
        display_region.setActive(True)
        display_region.setCamera(self.shadow_cam_np)

        # main shader
        self.main_shader = Shader.load(lang = Shader.SL_GLSL, vertex = "shaders/main_vert.glsl", fragment = "shaders/main_frag.glsl")

        ursina.render.setShaderInput("shadowMap", shadow_tex)
        ursina.render.setShaderInput("shadowCam", self.shadow_cam_np)
        ursina.render.setShaderInput("shadowDir", sun_direction)
        ursina.render.setShaderInput("shadowSize", (shadow_size, shadow_height, shadow_resolution))
        ursina.render.setShaderInput("shadowBias", shadow_bias)
        ursina.render.setShaderInput("shadowFilterResolution", (shadow_filter_radius, shadow_filter_samples))
        ursina.render.setShaderInput("softShadows", soft_shadows)

        shadow_texel_size = shadow_size / shadow_resolution
        shadow_texel_radius = sqrt(shadow_texel_size**2 + shadow_texel_size**2) / 2.0
        ursina.render.setShaderInput("shadowTexelRadius", shadow_texel_radius)

        ursina.render.setShaderInput("sunColor", sun_color)
        ursina.render.setShaderInput("ambientColor", ambient_color)

        noise_tex = createNoiseTexture(128)
        ursina.render.setShaderInput("noiseTex", noise_tex)

        ursina.render.setShaderInput("gamma", gamma)

        main_camera_initializer = NodePath(PandaNode("main camera initializer"))
        main_camera_initializer.setShader(self.main_shader)
        ursina.cam.node().setInitialState(main_camera_initializer.getState())

        # shadow shader
        self.shadow_shader = Shader.load(lang = Shader.SL_GLSL, vertex = "shaders/shadow_vert.glsl", fragment = "shaders/shadow_frag.glsl")

        shadow_camera_initializer = NodePath(PandaNode("shadow camera initializer"))
        shadow_camera_initializer.setShader(self.shadow_shader)
        self.shadow_cam.setInitialState(shadow_camera_initializer.getState())

        # debug shadow buffer
        # ursina.accept("v", ursina.bufferViewer.toggleEnable)


    def update(self):
        self.shadow_cam_np.setPos(self.player.world_position + camera.forward.normalized() * self.shadow_camera_direction_offset)