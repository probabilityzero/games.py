#version 120

uniform vec2 iResolution;
uniform float iTime;
uniform int uSnakeLen;
uniform vec2 uSnake[256];
uniform vec2 uFood;
uniform vec2 uGridSize;

float roundedBoxSDF(vec2 p, vec2 b, float r){
    vec2 d = abs(p) - b;
    return length(max(d, vec2(0.0))) - r;
}

void main(){
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    // aspect-correct grid coords
    vec2 gs = uGridSize;
    vec2 gp = uv * gs;

    vec3 col = vec3(0.02, 0.02, 0.04);

    // simple truchet-inspired background: rotated checker with subtle noise
    vec2 id = floor(gp);
    vec2 f = fract(gp) - 0.5;
    float hv = mod(id.x + id.y, 2.0);
    float bg = mix(0.12, 0.22, hv);
    col += vec3(bg * 0.6, bg * 0.8, bg);

    // draw snake segments
    float segGlow = 0.0;
    for(int i=0;i<256;i++){
        if(i>=uSnakeLen) break;
        vec2 s = uSnake[i];
        float d = length(gp - s);
        float r = 0.5; // radius in grid units
        float a = smoothstep(r, r-0.15, d);
        // head brighter
        if(i==0){
            vec3 hc = vec3(1.0, 0.9, 0.3);
            col = mix(col, hc, 1.0 - a);
            segGlow += (1.0 - a) * 0.9;
        } else {
            vec3 sc = vec3(0.1, 0.9, 0.3);
            col = mix(col, sc, 1.0 - a);
            segGlow += (1.0 - a) * 0.5;
        }
    }

    // food
    float df = length(gp - uFood);
    float af = smoothstep(0.6, 0.45, df);
    col = mix(col, vec3(1.0,0.2,0.2), 1.0 - af);

    // vignette and glow
    float v = pow(1.0 - length((uv - 0.5) * vec2(iResolution.x / iResolution.y, 1.0)), 1.5);
    col *= mix(0.9, 1.0, v);

    gl_FragColor = vec4(col,1.0);
}
