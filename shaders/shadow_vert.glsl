#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_Color;
attribute vec2 p3d_MultiTexCoord0;

varying vec4 color;
varying vec2 uv;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    color = p3d_Color;
    uv = p3d_MultiTexCoord0;
}