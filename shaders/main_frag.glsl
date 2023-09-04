#version 120

#define PI 3.14159

varying vec3 fragPos;
varying vec3 normal;
varying vec4 color;
varying vec2 uv;
varying vec4 fragPosLight;

uniform vec4 p3d_ColorScale;
uniform sampler2D p3d_Texture0;

uniform sampler2D shadowMap;
uniform vec3 shadowDir;
uniform vec3 shadowSize;
uniform float shadowTexelRadius;
uniform float shadowBias;
uniform bool softShadows;

uniform vec4 sunColor;
uniform vec4 ambientColor;

uniform sampler2D noiseTex;

uniform float gamma;
uniform vec2 shadowFilterResolution;


float rnd_index = 0.0;
float randomNumber()
{
    vec2 uv = rnd_index * vec2(253.47, 121.33);
    rnd_index += 1.3;
    return texture2D(noiseTex, uv).r;
}

// Narkowicz 2015, "ACES Filmic Tone Mapping Curve"
vec3 ACESFilm(vec3 x)
{
    float a = 2.51;
    float b = 0.03;
    float c = 2.43;
    float d = 0.59;
    float e = 0.14;
    return clamp((x*(a*x+b))/(x*(c*x+d)+e), 0.0, 1.0);
}


float calculateSoftShadow(vec3 norm, vec3 shadow_dir)
{
    vec3 proj_coords = fragPosLight.xyz / fragPosLight.w;
    proj_coords = proj_coords * 0.5 + 0.5;
    proj_coords.z = min(proj_coords.z, 1.0);

    float normal_bias = tan(acos(dot(norm, -shadow_dir))) * shadowTexelRadius * shadowFilterResolution.x * 2.0 + shadowBias;
    normal_bias /= shadowSize.y * 2.0;

    float texel_size = 1.0 / shadowSize.z;
    float shadow = 0.0;

    for (int i = int(shadowFilterResolution.x); i > 0; i--)
    {
        for (int j = 0; j < int(shadowFilterResolution.y); j++)
        {
            float angle = ((float(j) + randomNumber() * 2.0 - 0.5) / shadowFilterResolution.y) * 2.0 * PI;
            vec2 sample_coords = proj_coords.xy + vec2(sin(angle), cos(angle)) * texel_size * (i + randomNumber() * 2.0 - 1.0);

            float shadow_depth = texture2D(shadowMap, sample_coords).r;
            shadow += proj_coords.z - normal_bias < shadow_depth ? 1.0 : 0.0;
        }

        if (shadow == 0.0 || (shadow == shadowFilterResolution.y && i == int(shadowFilterResolution.x)))
        {
            shadow = shadowFilterResolution.x * shadowFilterResolution.y * min(shadow, 1.0);
            break;
        }
    }
    shadow /= shadowFilterResolution.x * shadowFilterResolution.y;

    return shadow;
}

float calculateHardShadow(vec3 norm, vec3 shadow_dir)
{
    vec3 proj_coords = fragPosLight.xyz / fragPosLight.w;
    proj_coords = proj_coords * 0.5 + 0.5;
    proj_coords.z = min(proj_coords.z, 1.0);

    float normal_bias = tan(acos(dot(norm, -shadow_dir))) * shadowTexelRadius + shadowBias;
    normal_bias /= shadowSize.y * 2.0;

    float shadow_depth = texture2D(shadowMap, proj_coords.xy).r;
    float shadow = proj_coords.z - normal_bias < shadow_depth ? 1.0 : 0.0;

    return shadow;
}


void main()
{
    vec3 norm = normalize(normal);
    vec3 shadow_dir = normalize(shadowDir);

    rnd_index = fragPos.x + fragPos.y + fragPos.z;

    // shadows
    float shadow = 0.0;
    if (softShadows)
        shadow = calculateSoftShadow(norm, shadow_dir);
    else
        shadow = calculateHardShadow(norm, shadow_dir);


    vec3 ambient = ambientColor.rgb * ambientColor.a;
    vec3 diffuse = max(dot(norm, -shadow_dir), 0.0) * sunColor.rgb * sunColor.a * shadow;

    vec3 lighting_result = ambient + diffuse;

    gl_FragColor = texture2D(p3d_Texture0, uv) * color * p3d_ColorScale;
    gl_FragColor.rgb *= lighting_result;

    // tonemapping + gamma correction
    // gl_FragColor.rgb = vec3(1.0) - exp(-gl_FragColor.rgb * exposure);
    gl_FragColor.rgb = ACESFilm(gl_FragColor.rgb);
    gl_FragColor.rgb = pow(gl_FragColor.rgb, vec3(1.0 / gamma));
}