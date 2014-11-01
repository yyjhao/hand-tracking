var drawline = function(from, to, material) {
    var geometry;
    geometry = new THREE.Geometry();
    geometry.vertices[0] = new THREE.Vector3(from[0], from[1], from[2]);
    geometry.vertices[1] = new THREE.Vector3(to[0], to[1], to[2]);
    return new THREE.Line(geometry, material, THREE.LineStrip);
};

var renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor( 0xffffff, 1);
document.body.appendChild(renderer.domElement);
var camera = new THREE.PerspectiveCamera(25, window.innerWidth / window.innerHeight, -10, 100);
camera.position.z = 1000;
var controls = new THREE.OrbitControls(camera);

var display = null;
function setVectors(points, handPoints) {
    if (display) {
        display.unbind();
    }

    display = init(points, handPoints);

    display.render();
    return display;
}

var init = function(zs, hand) {

    var alpha = 1;
    var aspect = window.innerWidth / window.innerHeight;
    var scene = new THREE.Scene();

    var geometry = new THREE.BufferGeometry();

    var positions = new Float32Array( zs.length*3 );
    var colors = new Float32Array( zs.length*3 );

    zs.forEach(function(p, k) {
        if (p > 400) return;
        positions[ 3 * k ] = k % 320 - 160;
        positions[ 3 * k + 1 ] = 239 - Math.floor(k / 320) - 120;
        positions[ 3 * k + 2 ] = p;

        colors[ 3*k ] = 1;
        colors[ 3*k + 1 ] = 0;
        colors[ 3*k + 2 ] = 0;
    });
    geometry.addAttribute( 'position', new THREE.BufferAttribute( positions, 3 ) );
    geometry.addAttribute( 'color', new THREE.BufferAttribute( colors, 3 ) );
    geometry.computeBoundingBox();

    var material = new THREE.PointCloudMaterial( { size: 4, vertexColors: THREE.VertexColors } );
    var cloud = new THREE.PointCloud(geometry, material);

    scene.add(cloud);

    var group = new THREE.Object3D();

    hand.forEach(function(line) {
        var color = new THREE.Color();
        color.setHSL(line.color, 0.8, 0.4);
        var material = new THREE.LineBasicMaterial({
            color: color,
            dashSize: 3,
            gapSize: 1,
            linewidth: 20
        });
        group.add(drawline(line.from, line.to, material));
    });

    scene.add(group);
    
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

function connect_points(points) {
    var connections = [
        [0, 1],
        [1, 2],
        [2, 3],
        [0, 4],
        [4, 5],
        [5, 6],
        [6, 7],
        [0, 8],
        [8, 9],
        [9, 10],
        [10, 11],
        [0, 12],
        [12, 13],
        [13, 14],
        [14, 15],
        [0, 16],
        [16, 17],
        [17, 18],
        [18, 19]
    ];

    return connections.map(function(conn) {
        return {
            from: points[conn[0]],
            to: points[conn[1]],
            color: 10
        };
    });
}

$.when($.get('/temp'), $.get('/result')).done(function(points, handPoints) {
    var ps = points[0].trim().split("\n").map(function(line) {
        return line.trim().split(" ").map(function(num) {
            return parseInt(num);
        });
    });

    var data = handPoints[0].trim().split("\n").map(function(line) {
        var nums = line.trim().split(/,\s*/).map(function(num) {
            return parseFloat(num);
        });
        var result = [];
        for (var i = 0; i < nums.length / 3; i++) {
            result.push([
                nums[i * 3],
                nums[i * 3 + 1],
                -nums[i * 3 + 2]
            ]);
        }
        return result;
    }).map(function(points) {
        return connect_points(points);
    });


    var ind = 0;
    setVectors(ps[0], data[0]);

    $(window).keypress(function(e) {
        if (e.keyCode == 0 || e.keyCode == 32) {
            ind += 2;
            setVectors(ps[ind], data[ind/2]);
        }
    });
});
