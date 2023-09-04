#version 120

varying vec2 uv;

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;

uniform float gamma;

vec3 ACESFilm(vec3 x)
{
    float a = 2.51;
    float b = 0.03;
    float c = 2.43;
    float d = 0.59;
    float e = 0.14;
    return clamp((x*(a*x+b))/(x*(c*x+d)+e), 0.0, 1.0);
}

void main()
{
    gl_FragColor.rgb = texture2D(p3d_Texture0, uv).rgb * p3d_ColorScale.rgb * p3d_ColorScale.a;

    // tonemapping + gamma correction
    // gl_FragColor.rgb = vec3(1.0) - exp(-gl_FragColor.rgb * exposure);
    gl_FragColor.rgb = ACESFilm(gl_FragColor.rgb);
    gl_FragColor.rgb = pow(gl_FragColor.rgb, vec3(1.0 / gamma));

    gl_FragColor.a = 1.0;
}