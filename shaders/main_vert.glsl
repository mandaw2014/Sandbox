#version 120

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_Color;
attribute vec2 p3d_MultiTexCoord0;

varying vec3 fragPos;
varying vec3 normal;
varying vec4 color;
varying vec2 uv;
varying vec4 fragPosLight;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelMatrixInverseTranspose;

uniform mat4 trans_world_to_clip_of_shadowCam;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    fragPos = vec3(p3d_ModelMatrix * p3d_Vertex);
	normal = mat3(p3d_ModelMatrixInverseTranspose) * p3d_Normal;
    color = p3d_Color;
	uv = p3d_MultiTexCoord0;
    fragPosLight = trans_world_to_clip_of_shadowCam * vec4(fragPos, 1.0);
}