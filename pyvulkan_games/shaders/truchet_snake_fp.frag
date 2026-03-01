#version 120

uniform vec2 iResolution;
uniform float iTime;
uniform int uSnakeLen;
uniform vec3 uSnake[128];
uniform vec3 uFood;
uniform vec3 uStartPos;
uniform vec3 uBackgroundColor;
uniform vec3 iCameraPos;
uniform vec3 iCameraDir;

const float MAX_DIST = 100.0;
const float MIN_DIST = 0.001;

float sdSphere(vec3 p, float r){ return length(p)-r; }

float sdCapsule(vec3 p, vec3 a, vec3 b, float r){
    vec3 pa = p - a;
    vec3 ba = b - a;
    float h = clamp(dot(pa,ba)/dot(ba,ba), 0.0, 1.0);
    return length(pa - ba*h) - r;
}

float mapScene(vec3 p){
    float d = 1e5;
    float r = 0.35; // snake radius
    // snake segments as capsules between consecutive points with small wobble
    for(int i=0;i<127;i++){
        if(i+1 >= uSnakeLen) break;
        vec3 a = uSnake[i];
        vec3 b = uSnake[i+1];
        // wobble offset per-segment
        float f = 3.0 + float(i)*0.12;
        float amp = 0.06 + mod(float(i),4.0)*0.01;
        vec3 off = vec3(sin(iTime*f + float(i))*amp, cos(iTime*(f*0.8) + float(i))*amp*0.5, 0.0);
        vec3 a2 = a + off;
        vec3 b2 = b + off;
        float c = sdCapsule(p, a2, b2, r);
        if(c < d) d = c;
    }
    // tip sphere at head
    if(uSnakeLen>0){
        float s = sdSphere(p - uSnake[0], r);
        d = min(d, s);
    }
    // food - sphere slightly emissive
    float fd = sdSphere(p - uFood, 0.25);
    d = min(d, fd);
    // ground plane
    float ground = p.y + 1.0;
    d = min(d, ground);
    // starting point marker (small sphere)
    float spd = sdSphere(p - uStartPos, 0.18);
    d = min(d, spd);
    return d;
}

vec3 estimateNormal(vec3 p){
    float e = 0.001;
    return normalize(vec3(
        mapScene(p + vec3(e,0,0)) - mapScene(p - vec3(e,0,0)),
        mapScene(p + vec3(0,e,0)) - mapScene(p - vec3(0,e,0)),
        mapScene(p + vec3(0,0,e)) - mapScene(p - vec3(0,0,e))
    ));
}

vec3 shade(vec3 ro, vec3 rd){
    float t = 0.0;
    int steps = 0;
    float m = 0.0;
    for(int i=0;i<200;i++){
        vec3 p = ro + rd * t;
        float d = mapScene(p);
        if(d < MIN_DIST || t > MAX_DIST) break;
        t += d * 0.8;
        steps++;
    }
    vec3 col = uBackgroundColor;
    if(t < MAX_DIST){
        vec3 p = ro + rd * t;
        vec3 n = estimateNormal(p);
        float diff = clamp(dot(n, normalize(vec3(0.5,1.0,0.4))), 0.0, 1.0);
        float spec = pow(max(dot(reflect(-rd, n), vec3(0,0,1.0)), 0.0), 24.0);
        // color by whether close to food
        float fd = sdSphere(p - uFood, 0.25);
        if(abs(fd) < 0.02){
            col = vec3(1.0, 0.35, 0.35) * (0.7 + diff);
        } else {
            // truchet-like stripes using position on tube
            float stripes = abs(sin((p.x + p.z + iTime*2.0)*6.0));
            vec3 base = mix(vec3(0.05,0.6,0.25), vec3(0.15,0.9,0.4), stripes);
            col = base * (0.4 + 0.6*diff) + spec*0.5;
        }
    }
    else {
        // far background color
        col = uBackgroundColor;
    }
    // if hit start marker, tint
    float sdstart = sdSphere(ro + rd * t - uStartPos, 0.18);
    if(abs(sdstart) < 0.02) col = mix(col, vec3(0.8,0.7,0.2), 0.9);
    return clamp(col, 0.0, 1.0);
}

void main(){
    vec2 uv = (gl_FragCoord.xy*2.0 - iResolution.xy)/iResolution.y;
    vec3 ro = iCameraPos;
    vec3 fw = normalize(iCameraDir);
    vec3 right = normalize(cross(vec3(0.0,1.0,0.0), fw));
    vec3 up = cross(fw, right);
    float fov = 1.0;
    vec3 rd = normalize(fw + uv.x*right + uv.y*up);
    vec3 col = shade(ro, rd);
    gl_FragColor = vec4(col,1.0);
}
