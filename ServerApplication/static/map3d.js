// --- Helper functions ---
function setMeshHeight(mesh, height) {
    mesh.scale.y = height;
    mesh.updateMatrix();
}

// ------------------------------
// ---------- Controls ----------

function Controls(renderer, camera, scene, countries, container) {
    // --- Members ---
    this.mouseMode = -1;
    this.mouseStart = new THREE.Vector2();
    this.mouseEnd = new THREE.Vector2();
    this.sceneBoundingBox = new THREE.Box3();
    this.cameraControlPoint = new THREE.Vector3(0.0, 4.5, 0.0);
    this.renderer = renderer;
    this.camera = camera;
    this.scene = scene;
    this.countries = countries;
    this.mouseOver = null;
    this.infoDiv = document.createElement('div');

    // --- Initialization ---
    var _this = this;
    
    this.renderer.domElement.addEventListener('contextmenu', function (event) { event.preventDefault(); }, false);
    this.renderer.domElement.addEventListener('mousedown', function (event) { _this.mouseDown(event); }, false);
    this.renderer.domElement.addEventListener('mousemove', function (event) { _this.mouseMove(event); }, false);
    this.renderer.domElement.addEventListener('mouseup', function (event) { _this.mouseUp(event); }, false);
    this.renderer.domElement.addEventListener( 'mousewheel', function (event) {_this.mousewheel(event); }, false );
    this.renderer.domElement.addEventListener( 'DOMMouseScroll', function (event) {_this.mousewheel(event); }, false ); // For firefox
    container.appendChild(this.infoDiv);
    this.infoDiv.style.position = 'absolute';
    this.infoDiv.style.top = '300px';
    this.infoDiv.style.background = '#fff';
    this.infoDiv.innerHTML = 'testi';
    
    // --- Methods ---
    this.update = function() {
        var mouseChange = new THREE.Vector2();
        mouseChange.copy(this.mouseEnd).sub(this.mouseStart);
        
        var speed = this.cameraControlPoint.y;
        
        switch (this.mouseMode) {
        case 0: // Left button - Drag
            this.cameraControlPoint.x -= mouseChange.x * speed;
            this.cameraControlPoint.z += mouseChange.y * speed;
            break;
            
        case 1: // Middle button - Zoom
            this.cameraControlPoint.y += mouseChange.y * speed;
            break;
            
        case 2: // Right button - Rotate
            this.camera.rotation.x += mouseChange.y * 3.14 * 0.75;
            if (this.camera.rotation.x > 0)
                this.camera.rotation.x = 0;
            if (this.camera.rotation.x < -3.14)
                this.camera.rotation.x = -3.14;
                this.camera.rotation.y -= mouseChange.x * 3.14 * 0.75;
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
    
    this.selectObject = function (x,y) { 
        direction = new THREE.Vector3(x, y, this.camera.near);
        direction.unproject(camera);
        direction.sub(camera.position);
        direction.normalize();
        ray = new THREE.Raycaster(this.camera.position, direction);
        intersects = ray.intersectObjects(scene.children);
        if (this.mouseOver) {
            this.mouseOver.material.emissive = new THREE.Color(0x000000);
	    this.mouseOver = null;
	}
        if (intersects[0]) {
            this.mouseOver = intersects[0].object;
            this.mouseOver.material.emissive = new THREE.Color(0x00ff00);
	    center = this.mouseOver.geometry.boundingBox.center();
	    center.y = 0;
	    screenPosition = this.fromWorldToScreen(center);
	    this.infoDiv.style.left = screenPosition.x + 'px';
	    this.infoDiv.style.top = screenPosition.y + 'px';
        }
    };

    this.fromWorldToScreen = function (point) {
	point.project(camera);
	x = (point.x + 1) / 2;
	y = (point.y + 1) / 2;
	var rect = this.renderer.domElement.getBoundingClientRect();
	x = x * rect.width;
	y = (1-y) * rect.height;
	return new THREE.Vector2(x, y);	
    };

    this.mousewheel = function (event) {
        event.preventDefault();
        event.stopPropagation();
        this.cameraControlPoint.y -= event.wheelDelta * 0.003;
    };

    this.getMouseOnElement = function(elem, clientX, clientY) {
        var rect = elem.getBoundingClientRect();
        x = ( (clientX- rect.left) / rect.width ) * 2 - 1;
        y = - ( (clientY - rect.top) / rect.height ) * 2 + 1;
        return new THREE.Vector2(x,y);
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
        mousePosition = this.getMouseOnElement(this.renderer.domElement, event.clientX, event.clientY);        
        this.mouseEnd.copy(mousePosition);
        this.selectObject(mousePosition.x, mousePosition.y);
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
    this.countries = {};
    this.controls = new Controls(this.renderer, this.camera, this.scene, this.countries, this.container);
    this.defaultHeight = 0.01;
    this.defaultColor = 0x222222;
    this.heightRange = new Range(0.01, 1.0);
    this.colorRange = new Range(0x666666, 0xFFFFFF);
    this.colorData = {};
    this.heightData = {};
    
    function lerp(x, y, t) {
        return (x & 0xFF) * (1.0 - t) + (y & 0xFF) * t;
    };
    
    this.normalizeData = function (data) {
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
        normalized_data["min_value"] = min_value;
        normalized_data["max_value"] = max_value;
        return normalized_data;
    };
    
    // --- Methods ---
    this.resize = function () {
        var w = this.container.clientWidth;
        var h = this.container.clientHeight;
        this.renderer.setSize(w, h);
        this.camera.aspect = w / h;
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
            geometry.computeBoundingSphere();
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

    this.hideCountriesWithNoData = function () {
        for (var name in this.countries) {
            if (this.countries.hasOwnProperty(name)) {
                if (this.colorData.hasOwnProperty(name) || this.heightData.hasOwnProperty(name)) {
                    this.countries[name].visible = true;
                }
                else this.countries[name].visible = false;
            }
        }
    };

    this.changeBackgroundColor = function (color) {
        this.renderer.setClearColor(color);
    }

    this.showAllCountries = function () {
        for (var name in this.countries) {
            if (this.countries.hasOwnProperty(name)) {
                 this.countries[name].visible = true;
            }
        }
    };

    this.ColorChangedCountriesWithNoData = function (color) {
        this.defaultColor = color;
            for (var name in this.countries) {
                if (this.countries.hasOwnProperty(name)) {
                    if (!this.colorData.hasOwnProperty(name)) {
                       this.setCountryColorRaw(name, color)
                }
            }
        }
    }

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

    this.normalizeData = function (data) {
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
        //TODO: fix this
        if(typeof min_value === "undefined") {
            min_value = 0;
            max_value = 0;
        }
        normalized_data["min_value"] = min_value;
        normalized_data["max_value"] = max_value;
        return normalized_data;
    };

    this.setHeightData = function (data) {
        for (var name in this.countries) {
            this.setCountryHeightRaw(name, this.defaultHeight);
        }
        this.heightData = this.normalizeData(data);
        for (var name in this.heightData) {
            this.setCountryHeight(name, this.heightData[name]);
        }
    };

    this.updateHeights = function () {
        for (var name in this.heightData) {
            this.setCountryHeight(name, this.heightData[name]);
        }
    };

    this.getColorDataMin = function () {
        if (this.colorData.hasOwnProperty("min_value"))
            return this.colorData["min_value"];
        return 0;
    };

    this.getColorDataMax = function () {
        if (this.colorData.hasOwnProperty("max_value"))
            return this.colorData["max_value"];
        return 0;
    };

    this.setColorData = function (data) {
        for (var name in this.countries) {
            this.setCountryColorRaw(name, this.defaultColor);
        }
        this.colorData = this.normalizeData(data);
        for (var name in this.colorData) {
            this.setCountryColor(name, this.colorData[name]);
        }
    };
    
    this.updateColors = function () {
        for (var name in this.colorData) {
            this.setCountryColor(name, this.colorData[name]);
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
    this.container.appendChild(this.renderer.domElement);

    var ambientLight = new THREE.AmbientLight(0x080C10);
    this.scene.add(ambientLight);

    var directionalLight1 = new THREE.DirectionalLight(0xFFD0D0, 1.0);
    directionalLight1.position.set(1.0, 1.0, -1.0);
    this.scene.add(directionalLight1);

    var directionalLight2 = new THREE.DirectionalLight(0xD0D0FF, 1.0);
    directionalLight2.position.set(-1.0, 1.0, 1.0);
    this.scene.add(directionalLight2);

    // canvas = document.createElement('canvas');
    // context = canvas.getContext('2d');
    // context.font = "20px Arial";

    // context.fillStyle = "#FFFFFF";
    // context.fillRect(0,0,150,20);
    // context.fillStyle = "#000000";
    // context.fillText('Hello, world!', 10, 17);
    
    // texture = new THREE.Texture(canvas);
    // texture.needsUpdate = true;
	
    // var spriteMaterial = new THREE.SpriteMaterial( { map: texture, useScreenCoordinates: true } );
	
    // sprite = new THREE.Sprite( spriteMaterial );
    // sprite.scale.set(1,1,1.0);
    // sprite.position.set( 0, 2, 0 );
    // this.scene.add( sprite );
}
