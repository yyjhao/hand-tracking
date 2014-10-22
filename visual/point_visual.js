var drawsphere = function(point) {
    var sphere = new THREE.Mesh(new THREE.SphereGeometry(point[0], point[1], point[2]), new THREE.MeshNormalMaterial());
    sphere.overdraw = true;
    return sphere;
};

var renderer = new THREE.SVGRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
var camera = new THREE.PerspectiveCamera(25, window.innerWidth / window.innerHeight, 1000, 3000);
camera.position.z = 50;
var controls = new THREE.OrbitControls(camera);


var drawline = function(from, to, material) {
    var geometry;
    geometry = new THREE.Geometry();
    geometry.vertices[0] = new THREE.Vector3(from[0], from[1], from[2]);
    geometry.vertices[1] = new THREE.Vector3(to[0], to[1], to[2]);
    return new THREE.Line(geometry, material, THREE.LineStrip);
};

function getOther(p) {
    return [p[0], p[1], p[2] + 100];
}

var init = function(boxsize, points) {

    var alpha = 1;
    var aspect = window.innerWidth / window.innerHeight;
    var scene = new THREE.Scene();
    var group = new THREE.Object3D();

    points.forEach(function(p) {
        var color = new THREE.Color();
        color.setHSL(0.4, 0.8, 0.4);
        var material = new THREE.LineBasicMaterial({
            color: color,
            dashSize: 3,
            gapSize: 1,
            linewidth: 20
        });
        group.add(drawline(p, getOther(p), material));

        // group.add(drawsphere(line.from));
        // group.add(drawsphere(line.to));
    });

    scene.add(group);
    // group.rotation.x = 3.1415 * (-0.5);
    // group.position.x = -5;
    // group.position.y = -5;
    
    var render = function() {
        return renderer.render(scene, camera);
    };
    controls.addEventListener('change', render);
    unbind = function() {
        controls.removeEventListener('change', render);
    };
    
    return {
        render: render,
        unbind: unbind
    };
};

function normalize(points, ref_points) {
    if (!ref_points) {
        ref_points = points;
    }
    var aves = [0, 0, 0];
    ref_points.forEach(function(p) {
        for (var i = 0; i < 3; i++) {
            aves[i] += p[i];
        }
    });

    aves = aves.map(function(n) {
        return n / ref_points.length;
    });

    return points.map(function(p) {
        return [
            p[0] - aves[0],
            p[1] - aves[1],
            p[2] - aves[2]
        ];
    });
}

$.get('/temp').done(function(points){
    var ps = points.split("\n").map(function(line) {
        return line.split(" ").map(function(num) {
            return parseInt(num);
        });
    }).filter(function(p) {
        return p[2] < 30000
    });
    // console.log(ps.length);
    console.log( ps.slice(0, 100))
    init(10, ps.slice(0, 100));
});
