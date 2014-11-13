
// ------------------------------
// ---------- Controls ----------

function Controls(renderer, camera) {
    // --- Members ---
    this.mouseMode = -1;
    this.mouseStart = new THREE.Vector2();
    this.mouseEnd = new THREE.Vector2();
    this.sceneBoundingBox = new THREE.Box3();
    this.cameraControlPoint = new THREE.Vector3(0.0, 4.5, 0.0);
    this.renderer = renderer;
    this.camera = camera;
    
    // --- Initialization ---
    var _this = this;
    
    this.renderer.domElement.addEventListener('contextmenu', function (event) { event.preventDefault(); }, false);
    this.renderer.domElement.addEventListener('mousedown', function (event) { _this.mouseDown(event); }, false);
    this.renderer.domElement.addEventListener('mousemove', function (event) { _this.mouseMove(event); }, false);
    this.renderer.domElement.addEventListener('mouseup', function (event) { _this.mouseUp(event); }, false);
    this.renderer.domElement.addEventListener( 'mousewheel', function (event) {_this.mousewheel(event); }, false );
    this.renderer.domElement.addEventListener( 'DOMMouseScroll', function (event) {_this.mousewheel(event); }, false ); // For firefox
    
    // --- Methods ---
    this.update = function() {
        var mouseChange = new THREE.Vector2();
        mouseChange.copy(this.mouseEnd).sub(this.mouseStart);
        
        // this.camera.rotation.x = -3.14 * 0.5;
        // this.camera.rotation.y = 0.0;
        // this.camera.rotation.z = 0.0;
        
        var speed = this.cameraControlPoint.y;
        
        switch (this.mouseMode) {
        case 0: // Left button - Drag
            this.cameraControlPoint.x -= mouseChange.x * speed;
            this.cameraControlPoint.z -= mouseChange.y * speed;
            break;
            
        case 1: // Middle button - Zoom
            this.cameraControlPoint.y += mouseChange.y * speed;
            break;
            
        case 2: // Right button - Rotate
            this.camera.rotation.x -= mouseChange.y * 3.14 * 0.75;
            if (this.camera.rotation.x > 0)
                this.camera.rotation.x = 0;
            if (this.camera.rotation.x < -3.14)
                this.camera.rotation.x = -3.14;
                this.camera.rotation.y += mouseChange.x * 3.14 * 0.75;
            if (this.camera.rotation.y > 3.14 * 0.5)
                this.camera.rotation.y = 3.14 * 0.5;
            if (this.camera.rotation.y < -3.14 * 0.5)
                this.camera.rotation.y = -3.14 * 0.5;
            break;
        }
        
        this.sceneBoundingBox.clampPoint(this.cameraControlPoint, this.cameraControlPoint);
        this.camera.position.copy(this.cameraControlPoint);
        this.camera.position.y = 0.5;
        this.camera.position.add(this.camera.getWorldDirection().multiplyScalar(-this.cameraControlPoint.y));
        this.mouseStart.copy(this.mouseEnd);
    };
    
    this.mousewheel = function (event) {
        this.cameraControlPoint.y -= event.wheelDelta * 0.003;
    };

    this.getMouseOnElement = function(elem, pageX, pageY) {
        var rect = elem.getBoundingClientRect();
        return new THREE.Vector2(
            (pageX - rect.left) / rect.width,
            (pageY - rect.top) / rect.height
        );
    };
    
    this.mouseDown = function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        if (this.mouseMode >= 0)
            return;
        
        this.mouseMode = event.button;
        
        this.mouseStart.copy(this.getMouseOnElement(this.renderer.domElement, event.pageX, event.pageY));
        this.mouseEnd.copy(this.mouseStart);
    };
    
    this.mouseMove = function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        this.mouseEnd.copy(this.getMouseOnElement(this.renderer.domElement, event.pageX, event.pageY));
        //console.log(this.mouseEnd);
    };

    this.mouseUp = function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        if (event.button != this.mouseMode)
            return;
        
        this.mouseMode = -1;
    };
}

// ------------------------------
// ---------- Map3D -------------

function Range(min, max) {
    this.min = typeof min !== 'undefined' ? min : 0.0;
    this.max = typeof max !== 'undefined' ? max : 1.0;
}

function Map3D(parentElement) {
    // --- Members ---
    this.container = parentElement;
    this.stats = new Stats();
    this.renderer = new THREE.WebGLRenderer({antialias: false});
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75.0, 800.0/600.0, 0.1, 100.0);
    this.camera.rotation.x = -3.14 * 0.5;
    this.controls = new Controls(this.renderer, this.camera);
    this.countries = {};
    this.defaultHeight = 0.01;
    this.defaultColor = 0x222222;
    this.heightRange = new Range(0.01, 1.0);
    this.colorRange = new Range(0x666666, 0xFFFFFF);
    this.colorData = undefined;
    this.heightData = undefined;
    // --- Helper functions ---
    function setMeshHeight(mesh, height) {
        mesh.scale.y = height;
        mesh.updateMatrix();
    }
    
    // --- Methods ---
    this.onResize = function (event) {
        var rect = this.container.getBoundingClientRect();
        var screenW = rect.width;
        var screenH = rect.height;
        this.renderer.setSize(screenW, screenH);
        this.camera.aspect = screenW / screenH;
        this.camera.updateProjectionMatrix();
    };
    
    this.setMapData = function (mapData) {
        var sceneBoundingBox = this.controls.sceneBoundingBox;
        
        var loader = new THREE.JSONLoader;
        for (var index in mapData) {
            country = mapData[index];
            
            var name = country[0];
            var data = country[1];
            
            var geometry = loader.parse(data, "").geometry;
            geometry.computeBoundingBox();
            sceneBoundingBox.union(geometry.boundingBox);
            var material = new THREE.MeshLambertMaterial( { color: this.defaultColor } );
            var mesh = new THREE.Mesh(geometry, material);
            setMeshHeight(mesh, this.defaultHeight);
            
            this.scene.add(mesh);
            this.countries[name] = mesh;
        }
        
        sceneBoundingBox.min.y = 1.2;
        sceneBoundingBox.max.y = 3.5;
        
        this.render();
    };
    
    this.clear = function () {
        for (var name in this.countries) {
            if (this.countries.hasOwnProperty(name)) {
                var mesh = this.countries[name];
                setMeshHeight(mesh, this.defaultHeight);
                mesh.material.setValues( { color: this.defaultColor } );
            }
        }
    };
    
    this.setDefaultHeight = function (height) {
        this.defaultHeight = height;
    };
    
    this.setDefaultColor = function (color) {
        this.defaultColor = color;
    };
    
    this.setHeightRange = function (min, max) {
        this.heightRange.min = min;
        this.heightRange.max = max;
    };
    
    this.setColorRange = function (min, max) {
        this.colorRange.min = min;
        this.colorRange.max = max;
    };
    
    this.setCountryHeight = function (name, height) {
        if (this.countries.hasOwnProperty(name)) {
            var mesh = this.countries[name];
            var distance = this.heightRange.max - this.heightRange.min;
            setMeshHeight(mesh, this.heightRange.min + distance * height);
        }
    };
    
    function lerp(x, y, t) {
        return (x & 0xFF) * (1.0 - t) + (y & 0xFF) * t;
    };
    
    this.setCountryColor = function (name, color) {
        if (this.countries.hasOwnProperty(name)) {
            var mesh = this.countries[name];
            
            var color0 = this.colorRange.min;
            var color1 = this.colorRange.max;
            var f = color;
            
            var r = lerp(color0 >> 16, color1 >> 16, f) & 0xFF;
            var g = lerp(color0 >> 8, color1 >> 8, f) & 0xFF;
            var b = lerp(color0, color1, f) & 0xFF;
            var c = (r << 16) | (g << 8) | b;
            
            mesh.material.setValues( { color: c } );
        }
    };
    
    this.setCountry = function (name, height, color) {
        this.setCountryHeight(height);
        this.setCountryColor(color);
    };
    
    this.setCountryHeightRaw = function (name, height) {
        if (this.countries.hasOwnProperty(name)) {
            var mesh = this.countries[name];
            setMeshHeight(mesh, height);
        }
    };
    
    this.setCountryColorRaw = function (name, color) {
        if (this.countries.hasOwnProperty(name)) {
            var mesh = this.countries[name];
            mesh.material.setValues( { color: color } );
        }
    };
    
    this.normalize_data = function (data) {
        var normalized_data = {};
        var max_value;
        var min_value;
        for(key in data){
            if(data.hasOwnProperty(key) && this.countries.hasOwnProperty(key)){
                if (typeof max_value !== "undefined"){
                    if(data[key] > max_value) max_value = data[key];
                    if(data[key] < min_value) min_value = data[key];
                }
                else {
                    max_value = data[key];
                    min_value = data[key];
                }
            }
        }

        for(key in data){
            normalized_data[key] = ((data[key])-min_value)/(max_value-min_value);
        }
        return normalized_data;
    };
    
    this.setHeightData = function (data) {
        this.heightData = this.normalize_data(data);
        for (var name in this.heightData) {
            this.setCountryHeight(name, this.heightData[name]);
        }
    };

    this.updateHeights = function () {
        if (this.heightData) {
            for (var name in this.heightData) {
                this.setCountryHeight(name, this.heightData[name]);
            }
        }
    };
    
    this.setColorData = function (data) {
        this.colorData = this.normalize_data(data);
        for (var name in this.colorData) {
            this.setCountryColor(name, this.colorData[name]);
        }
    };
    
    this.updateColors = function () {
        if (this.colorData) {
            for (var name in this.colorData) {
                this.setCountryColor(name, this.colorData[name]);
            }
        }
    };

    this.setData = function (data) {
        this.clear();
        this.setHeightData(data.height);
        this.setColorData(data.color);
    };
    
    this.render = function () {
        var _this = this;
        requestAnimationFrame(function () { _this.render(); });
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
        this.stats.update();
    };
    
    // --- Initialization ---
    this.stats.domElement.style.position = 'absolute';
    this.container.appendChild(this.stats.domElement);

    this.renderer.setClearColor(0x335577);
    this.renderer.setSize(800, 600);
    this.container.appendChild(this.renderer.domElement);

    var ambientLight = new THREE.AmbientLight(0x080C10);
    this.scene.add(ambientLight);

    var directionalLight1 = new THREE.DirectionalLight(0xFFD0D0, 1.0);
    directionalLight1.position.set(1.0, 1.0, -1.0);
    this.scene.add(directionalLight1);

    var directionalLight2 = new THREE.DirectionalLight(0xD0D0FF, 1.0);
    directionalLight2.position.set(-1.0, 1.0, 1.0);
    this.scene.add(directionalLight2);

    this.onResize();
    
    var _this = this;
    window.addEventListener('resize', function (event) { _this.onResize(event); }, false);
}
