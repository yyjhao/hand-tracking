var drawline = function(from, to, material) {
    var geometry;
    geometry = new THREE.Geometry();
    geometry.vertices[0] = new THREE.Vector3(from[0], from[1], from[2]);
    geometry.vertices[1] = new THREE.Vector3(to[0], to[1], to[2]);
    return new THREE.Line(geometry, material, THREE.LineStrip);
};

var drawsphere = function(point) {
    var sphere = new THREE.Mesh(new THREE.SphereGeometry(point[0], point[1], point[2]), new THREE.MeshNormalMaterial());
    sphere.overdraw = true;
    return sphere;
};

var renderer = new THREE.SVGRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
var camera = new THREE.PerspectiveCamera(25, window.innerWidth / window.innerHeight, 1, 1000);
camera.position.z = 50;
var controls = new THREE.OrbitControls(camera);

var init = function(boxsize, vectors) {

    var alpha = 1;
    var aspect = window.innerWidth / window.innerHeight;
    var scene = new THREE.Scene();
    var group = new THREE.Object3D();

    vectors.forEach(function(line) {
        var color = new THREE.Color();
        color.setHSL(line.color, 0.8, 0.4);
        var material = new THREE.LineBasicMaterial({
            color: color,
            dashSize: 3,
            gapSize: 1,
            linewidth: 20
        });
        group.add(drawline(line.from, line.to, material));

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

var display = null;
function setVectors(vectors) {
    if (display) {
        display.unbind();
    }

    display = init(10, vectors);

    display.render();
    return display;
}

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

function truth_connect_points(points) {

// wrist, index_mcp, index_pip, index_dip, index_tip, middle_mcp, middle_pip,
// middle_dip, middle_tip, ring_mcp, ring_pip, ring_dip, ring_tip, little_mcp,
// little_pip, little_dip, little_tip, thumb_mcp, thumb_pip, thumb_dip, thumb_tip

    var connections = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 4],
        [0, 5],
        [5, 6],
        [6, 7],
        [7, 8],
        [0, 9],
        [9, 10],
        [10, 11],
        [11, 12],
        [0, 13],
        [13, 14],
        [14, 15],
        [15, 16],
        [0, 17],
        [17, 18],
        [18, 19],
        [19, 20]
    ];

    return connections.map(function(conn) {
        return {
            from: points[conn[0]],
            to: points[conn[1]],
            color: 0.3
        };
    });
}

$.when($.get('/subject1_truth.txt'), $.get('/yjunstable.txt')).done(function(r1, r2) {
    var content_truth = r1[0],
        content = r2[0];

    var data_truth = content_truth.split("\n").slice(1).map(function(line) {
        var nums = line.split(' ').map(function(num) {
            return parseFloat(num);
        });
        var result = [];
        for (var i = 0; i < nums.length / 3; i++) {
            result.push([
                nums[i * 3],
                nums[i * 3 + 1],
                nums[i * 3 + 2]
            ]);
        }
        return result;
    });

    var data = content.split("\n").map(function(line) {
        var nums = line.split(/,\s*/).map(function(num) {
            return parseFloat(num);
        });
        var result = [];
        for (var i = 0; i < nums.length / 3; i++) {
            result.push([
                nums[i * 3],
                nums[i * 3 + 1],
                nums[i * 3 + 2]
            ]);
        }
        return result;
    }).map(function(points, ind) {
        return normalize(points, data_truth[ind]);
    });

    data_truth = data_truth.map(function(points) {
        return normalize(points);
    });
    
    var data_vis = data.map(function(points) {
        return connect_points(points);
    });

    var data_truth_vis = data_truth.map(function(points) {
        return [];
        return truth_connect_points(points);
    });

    var ind = 0;
    setVectors(data_vis[0].concat(data_truth_vis[0]));

    $(window).keypress(function(e) {
        if (e.keyCode == 0 || e.keyCode == 32) {
            ind++;
            setVectors(data_vis[ind].concat(data_truth_vis[ind]));
        }
    });
});
