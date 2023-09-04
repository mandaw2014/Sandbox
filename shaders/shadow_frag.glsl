#version 120

varying vec4 color;
varying vec2 uv;

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

void main()
{
    gl_FragColor = texture2D(p3d_Texture0, uv) * p3d_ColorScale * color;
}