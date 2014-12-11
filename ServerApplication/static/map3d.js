// --- Helper functions ---
function setMeshHeight(mesh, height) {
    mesh.scale.y = height;
    mesh.updateMatrix();
}

function setMeshColor(mesh, color) {
    mesh.material.setValues( { color: color } );
    /*var threeColor = new THREE.Color(color);
    mesh.material.uniforms.color.value.x = threeColor.r;
    mesh.material.uniforms.color.value.y = threeColor.g;
    mesh.material.uniforms.color.value.z = threeColor.b;*/
}

function lerp(x, y, t) {
    return (x & 0xFF) * (1.0 - t) + (y & 0xFF) * t;
};

function computeFlatNormals(geometry) {
    geometry.computeFaceNormals();

    for (var i = 0; i < geometry.faces.length; i++) {
        face = geometry.faces[i];
            
        face.vertexNormals[0] = face.normal.clone();
        face.vertexNormals[1] = face.normal.clone();
        face.vertexNormals[2] = face.normal.clone();
        
        face.vertexNormals[0].y += 0.25;
        face.vertexNormals[1].y += 0.25;
        face.vertexNormals[2].y += 0.25;
        
        face.vertexNormals[0].normalize();
        face.vertexNormals[1].normalize();
        face.vertexNormals[2].normalize();
    }
}

// ------------------------------
// ---------- Controls ----------

function Controls(map) {
    // --- Members ---
    this.mouseMode = -1;
    this.mouseStart = new THREE.Vector2();
    this.mouseEnd = new THREE.Vector2();
    this.sceneBoundingBox = new THREE.Box3();
    this.cameraControlPoint = new THREE.Vector3(0.0, 4.5, 0.0);
    this.map = map;
    this.mouseOver = null;
    this.mouseOverHandler = function (countryID, countryName) {};
    this.infoDiv = document.createElement('div');
    this.lastMouseMove = Date.now();

    // --- Initialization ---
    var _this = this;
    
    this.map.renderer.domElement.addEventListener('contextmenu', function (event) { event.preventDefault(); }, false);
    this.map.renderer.domElement.addEventListener('mousedown', function (event) { _this.mouseDown(event); }, false);
    this.map.renderer.domElement.addEventListener('mousemove', function (event) { _this.mouseMove(event); }, false);
    this.map.renderer.domElement.addEventListener('mouseup', function (event) { _this.mouseUp(event); }, false);
    this.map.renderer.domElement.addEventListener('mousewheel', function (event) { _this.mousewheel(event); }, false);
    this.map.renderer.domElement.addEventListener('DOMMouseScroll', function (event) { _this.mousewheelFF(event); }, false); // For firefox
    
    document.body.appendChild(this.infoDiv);
    this.infoDiv.style.position = 'absolute';
    this.infoDiv.style.background = '#fff';
    this.infoDiv.id = 'map3d-info';
    this.infoDiv.style["white-space"] = "nowrap";
    
    // --- Methods ---
    this.update = function() {
        var mouseChange = new THREE.Vector2();
        mouseChange.copy(this.mouseEnd).sub(this.mouseStart);
        
        var speed = this.cameraControlPoint.y;
        
        switch (this.mouseMode) {
        case 0: // Left button - Rotate
            this.map.camera.rotation.x += mouseChange.y * 3.14 * 0.75;
            if (this.map.camera.rotation.x > 0)
                this.map.camera.rotation.x = 0;
            if (this.map.camera.rotation.x < -3.14)
                this.map.camera.rotation.x = -3.14;
                this.map.camera.rotation.y -= mouseChange.x * 3.14 * 0.75;
            if (this.map.camera.rotation.y > 3.14 * 0.5)
                this.map.camera.rotation.y = 3.14 * 0.5;
            if (this.map.camera.rotation.y < -3.14 * 0.5)
                this.map.camera.rotation.y = -3.14 * 0.5;
            break;

        case 2: // Right button - Drag
            this.cameraControlPoint.x -= mouseChange.x * speed;
            this.cameraControlPoint.z += mouseChange.y * speed;
            break;
            
        case 1: // Middle button - Zoom
            this.cameraControlPoint.y += mouseChange.y * speed;
            break;
        }
        
        this.sceneBoundingBox.clampPoint(this.cameraControlPoint, this.cameraControlPoint);
        this.map.camera.position.copy(this.cameraControlPoint);
        this.map.camera.position.y = 0.5;
        this.map.camera.position.add(this.map.camera.getWorldDirection().multiplyScalar(-this.cameraControlPoint.y));
        this.mouseStart.copy(this.mouseEnd);
    };
    
    this.onMouseOver = function () {
        for (var id in this.map.countries) {
            if (this.map.countries.hasOwnProperty(id)) {
                if (this.map.countries[id] === this.mouseOver) {
                    info = this.mouseOverHandler(id, this.mouseOver.name);
                    return info;
                }
            }
        }
        return null;
    }
    
    this.selectObject = function (event) { 
        var p = this.getMousePosition(event.clientX, event.clientY);
        direction = new THREE.Vector3(p.x, p.y, this.map.camera.near);
        direction.unproject(this.map.camera);
        direction.sub(this.map.camera.position);
        direction.normalize();
        
        var right = new THREE.Vector3();
        right.crossVectors(direction, this.map.camera.up);
        right.normalize();
        var up = new THREE.Vector3();
        up.crossVectors(direction, right);
        up.normalize();
        var origin = new THREE.Vector3();
        var r = new THREE.Vector3();
        var u = new THREE.Vector3();
        
        
        var selected = null;
        
        ray = new THREE.Raycaster(this.map.camera.position, direction);
        intersects = ray.intersectObjects(this.map.scene.children);
        if (intersects[0])
            selected = intersects[0].object;
            
        if (!selected) {
            var numCasts = 10;
            var distance = 0.02;
            
            var objects = [];
            for (var i = 0; i < numCasts; i++) {
                var angle = ((Math.PI * 2) / numCasts) * i;
                
                r.copy(right);
                r.multiplyScalar(Math.cos(angle) * distance);
                u.copy(up);
                u.multiplyScalar(Math.sin(angle) * distance);
                
                origin.copy(this.map.camera.position);
                origin.add(r);
                origin.add(u);
                
                ray = new THREE.Raycaster(origin, direction);
                intersects = ray.intersectObjects(this.map.scene.children);
                if (intersects[0])
                    objects.push(intersects[0].object);
            }
            
            if (objects.length > 0) {
                var counts = {};
                for (var i in objects) {
                    var obj = objects[i];
                    if (counts.hasOwnProperty(obj.name)) {
                        counts[obj.name].count += 1;
                    } else {
                        counts[obj.name] = { "count": 1, "object": obj };
                    }
                }
                
                var maxCount = 0;
                for (var name in counts) {
                    if (counts.hasOwnProperty(name)) {
                        if (counts[name].count > maxCount) {
                            maxCount = counts[name].count;
                            selected = counts[name].object;
                        }
                    }
                }
            }
        }
        
        if (this.mouseOver) {
            this.mouseOver.material.emissive = new THREE.Color(0x000000);
            this.mouseOver = null;
        }
        if (selected && this.mouseMode === -1) {
            this.mouseOver = selected;
            this.mouseOver.material.emissive = new THREE.Color(0x00ff00);
            
            var info = this.onMouseOver();
            if (info) {
                var scrollLeft = document.body.scrollLeft;
                var scrollTop = document.body.scrollTop;
                
                var x = event.clientX + scrollLeft;
                var y = event.clientY + scrollTop;
                
                var docWidth = document.documentElement.clientWidth;
                var docHeight = document.documentElement.clientHeight;
                
                this.infoDiv.style.left = (x + 20) + 'px';
                this.infoDiv.style.top = (y + 20) + 'px';
                
                this.infoDiv.innerHTML = info;
                this.infoDiv.style.display = 'initial';
                
                var rect2 = this.infoDiv.getBoundingClientRect();
                if (rect2.right > docWidth) {
                    this.infoDiv.style.left = (x - rect2.width - 20) + 'px';
                }
                if (rect2.bottom > docHeight) {
                    this.infoDiv.style.top = (docHeight - rect2.height + scrollTop) + 'px';
                }
            }
        } else {
            this.infoDiv.style.display = 'none';
        }
    };

    this.mousewheel = function (event) {
        event.preventDefault();
        event.stopPropagation();
        this.cameraControlPoint.y -= event.wheelDelta * 0.003;
    };
    
    this.mousewheelFF = function (event) {
        event.preventDefault();
        event.stopPropagation();
        this.cameraControlPoint.y -= event.detail * 0.3;
    }

    this.getMousePosition = function(clientX, clientY) {
        var elem = this.map.renderer.domElement;
        var rect = elem.getBoundingClientRect();
        x = ( (clientX - rect.left) / rect.width ) * 2 - 1;
        y = - ( (clientY - rect.top) / rect.height ) * 2 + 1;
        return new THREE.Vector2(x,y);
    };
    
    this.mouseDown = function(event) {
        event.preventDefault();
        event.stopPropagation();
        
        if (this.mouseMode >= 0)
            return;
        
        this.mouseMode = event.button;
        
        this.mouseStart.copy(this.getMousePosition(event.clientX, event.clientY));
        this.mouseEnd.copy(this.mouseStart);
    };
    
    this.mouseMove = function(event) {
        event.preventDefault();
        event.stopPropagation();
        mousePosition = this.getMousePosition(event.clientX, event.clientY);        
        this.mouseEnd.copy(mousePosition);
        this.selectObject(event);
	this.lastMouseMove = Date.now();
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
    this.renderer = new THREE.WebGLRenderer({
	antialias: true,
	preserveDrawingBuffer: true 
    });
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75.0, 800.0/600.0, 0.1, 100.0);
    this.camera.rotation.x = -3.14 * 0.5;
    this.countries = {};
    this.controls = new Controls(this);
    this.defaultHeight = 0.01;
    this.defaultColor = 0x222222;
    this.heightRange = new Range(0.01, 1.0);
    this.colorRange = new Range(0x666666, 0xFFFFFF);
    this.colorData = {};
    this.heightData = {};
    
    // --- Initialization ---
    
    /* Uncomment following lines to enable FPS-counter.
     * Stats.js library must be included for these to work.
     * https://github.com/mrdoob/stats.js/
     */
    // this.stats = new Stats();
    // this.stats.domElement.style.position = 'absolute';
    // this.container.appendChild(this.stats.domElement);
    
    this.renderer.setClearColor(0x335577);
    this.container.appendChild(this.renderer.domElement);

    var directionalLight1 = new THREE.DirectionalLight(0xFFFFFF, 0.8);
    directionalLight1.position.set(1.0, 1.0, -1.0);
    this.scene.add(directionalLight1);

    var directionalLight2 = new THREE.DirectionalLight(0xFFFFFF, 0.8);
    directionalLight2.position.set(-1.0, 1.0, 1.0);
    this.scene.add(directionalLight2);
    
    // --- Methods ---
    this.resize = function () {
        var w = this.container.clientWidth;
        var h = this.container.clientHeight;
        this.renderer.setSize(w, h);
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
    };
    
    this.setMouseOverHandler = function (handler) {
        this.controls.mouseOverHandler = handler;
    }
    
    this.computeNormals = function () {
        for (var id in this.countries) {
            if (this.countries.hasOwnProperty(id)) {
                var mesh = this.countries[id];
                computeFlatNormals(mesh.geometry);
            }
        }
    }

    this.clearScene = function () {
        var children = this.scene.children.slice(0);
        for (var index in children) {
            var child = children[index];
            if (child instanceof THREE.Mesh) {
                this.scene.remove(child);
            }
        }
    };

    this.setMapData = function (mapData) {
        var sceneBoundingBox = this.controls.sceneBoundingBox;

        this.clearScene();

        var loader = new THREE.JSONLoader;
        this.countries = {};
        for (var index in mapData) {
            country = mapData[index];
            
            var id = country[0];
            var name = country[1];
            var data = country[2];
            
            var geometry = loader.parse(data, "").geometry;
            geometry.computeBoundingBox();
            geometry.computeBoundingSphere();
            sceneBoundingBox.union(geometry.boundingBox);
            var material = new THREE.MeshLambertMaterial();
            var mesh = new THREE.Mesh(geometry, material);
            setMeshHeight(mesh, this.defaultHeight);
            setMeshColor(mesh, this.defaultColor);
            mesh.name = name;
            
            this.scene.add(mesh);
            this.countries[id] = mesh;
        }
        
        this.computeNormals();
        
        sceneBoundingBox.min.y = 1.2;
        sceneBoundingBox.max.y = 3.5;
        
        this.render();
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
        
        if (max_value - min_value < 0.00001)
            min_value = 0.0;

        for(key in data){
            if(data.hasOwnProperty(key))
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

    this.hideCountriesWithNoData = function () {
        for (var id in this.countries) {
            if (this.countries.hasOwnProperty(id)) {
                var visible = (this.colorData.hasOwnProperty(id) || this.heightData.hasOwnProperty(id));
                this.countries[id].visible = visible;
            }
        }
    };

    this.changeBackgroundColor = function (color) {
        this.renderer.setClearColor(color);
    };

    this.showAllCountries = function () {
        for (var id in this.countries) {
            if (this.countries.hasOwnProperty(id)) {
                 this.countries[id].visible = true;
            }
        }
    };

    this.ColorChangedCountriesWithNoData = function (color) {
        this.defaultColor = color;
        for (var id in this.countries) {
            if (!this.colorData.hasOwnProperty(id)) {
               this.setCountryColorRaw(id, color);
            }
        }
    };

    this.clear = function () {
        for (var id in this.countries) {
            if (this.countries.hasOwnProperty(id)) {
                var mesh = this.countries[id];
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
    
    this.setCountryHeight = function (id, height) {
        if (this.countries.hasOwnProperty(id)) {
            var mesh = this.countries[id];
            var distance = this.heightRange.max - this.heightRange.min;
            setMeshHeight(mesh, this.heightRange.min + distance * height);
        } else {
            //console.log("No country with id", id);
        }
    };
    
    this.setCountryColor = function (id, color) {
        if (this.countries.hasOwnProperty(id)) {
            var mesh = this.countries[id];
            
            var color0 = this.colorRange.min;
            var color1 = this.colorRange.max;
            var f = color;
            
            var r = lerp(color0 >> 16, color1 >> 16, f) & 0xFF;
            var g = lerp(color0 >> 8, color1 >> 8, f) & 0xFF;
            var b = lerp(color0, color1, f) & 0xFF;
            var c = (r << 16) | (g << 8) | b;
            
            setMeshColor(mesh, c);
        } else {
            //console.log("No country with id", id);
        }
    };
    
    this.setCountry = function (id, height, color) {
        this.setCountryHeight(height);
        this.setCountryColor(color);
    };
    
    this.setCountryHeightRaw = function (id, height) {
        if (this.countries.hasOwnProperty(id)) {
            var mesh = this.countries[id];
            setMeshHeight(mesh, height);
        }
    };
    
    this.setCountryColorRaw = function (id, color) {
        if (this.countries.hasOwnProperty(id)) {
            var mesh = this.countries[id];
            setMeshColor(mesh, color);
        }
    };
    
    this.setHeightData = function (data) {
        for (var id in this.countries) {
            this.setCountryHeightRaw(id, this.defaultHeight);
        }
        this.heightData = this.normalizeData(data);
        for (var id in this.heightData) {
            this.setCountryHeight(id, this.heightData[id]);
        }
    };

    this.updateHeights = function () {
        for (var id in this.heightData) {
            this.setCountryHeight(id, this.heightData[id]);
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
        for (var id in this.countries) {
            this.setCountryColorRaw(id, this.defaultColor);
        }
        this.colorData = this.normalizeData(data);
        for (var id in this.colorData) {
            this.setCountryColor(id, this.colorData[id]);
        }
    };
    
    this.updateColors = function () {
        for (var id in this.colorData) {
            this.setCountryColor(id, this.colorData[id]);
        }
    };

    this.setData = function (data) {
        this.clear();
        this.setHeightData(data.height);
        this.setColorData(data.color);
    };
    
    this.render = function () {
        var _this = this;
	var renderFunction = function () { _this.render(); };
	if (this.controls.lastMouseMove + 500 > Date.now())
	    requestAnimationFrame(renderFunction);
	else {
            setTimeout(function () { requestAnimationFrame(renderFunction); },
		       500);    
	}

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
        // this.stats.update();
    };

    this.toPng = function (width, height) {
	this.renderer.setSize(width, height);
	this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
	this.renderer.render(this.scene, this.camera);
	var dataUrl = this.renderer.domElement.toDataURL("image/png");
	this.resize();
	return dataUrl;
    };
}
