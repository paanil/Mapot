var map;
var color_data = { "values": {}, "name": "", "unit": "" };
var height_data = { "values": {}, "name": "", "unit": "" };


function update_map_heights() {
    $('#currentValue').html(this.value);
    map.setHeightRange(0.05, this.value);
    map.updateHeights();
}

function update_map_colors(color) {
  var gradient_min = $('#minColor').spectrum("get").toHex();
  var gradient_max = $('#maxColor').spectrum("get").toHex();
  update_gradient(gradient_min, gradient_max);
  
  var color_min = parseInt(gradient_min, 16);
  var color_max = parseInt(gradient_max, 16);
  map.setColorRange(color_min, color_max);
  map.updateColors();
}

function update_gradient_min_max() {
  var min_value = map.getColorDataMin();
  var max_value = map.getColorDataMax();
  $('#grad-min').html(pretty_number(parseFloat(min_value)));
  $('#grad-max').html(pretty_number(parseFloat(max_value)));
}

function update_gradient(gradient_min, gradient_max) {
  $('#grad').css({'background': '-webkit-linear-gradient(left, #' + gradient_min+ ' , #' + gradient_max + ')'});
  $('#grad').css({'background': '-o-linear-gradient(right, #' + gradient_min + ' , #' + gradient_max + ')'});
  $('#grad').css({'background': '-moz-linear-gradient(right, #' +  gradient_min + ' , #' + gradient_max + ')'});
  $('#grad').css({'background': 'linear-gradient(to right, #' + gradient_min + ' , #' + gradient_max + ')'});
  update_gradient_min_max();
};

function update_map_visibilities() {
  if (document.getElementById('hide_countries').checked) {
    map.hideCountriesWithNoData();
  } else {
    map.showAllCountries();
  }
}

function update_map_background_color() {
  var background_color = parseInt($('#BackgroundColor').spectrum("get").toHex(), 16);
  map.changeBackgroundColor(background_color);
}

function update_map_dataless_countries_color() {
  var color_no_data = parseInt($('#NoDataColor').spectrum("get").toHex(), 16);
  map.ColorChangedCountriesWithNoData(color_no_data);
}


function send_color_query() {
  var color_selection = $("#color-select").val();
  var color_parameter = $("#color-param-select").val();
  $.getJSON("/_data", { id: color_selection, param: color_parameter },
            function(data) {
      color_data = data;
      map.setColorData(data.values);
      update_map_visibilities();
      update_gradient_min_max();
    });
  return false;
};

function send_height_query() {
  var height_selection = $("#height-select").val();
  var height_parameter = $("#height-param-select").val();
  $.getJSON("/_data", { id: height_selection, param: height_parameter },
            function(data) {
      height_data = data;
      map.setHeightData(data.values);
      update_map_visibilities();
    });
  return false;
};

function load_map_model(hd) {
  if (!hd) {
    $.getJSON('/static/world_map.json', {},
              function (data) {
        map.setMapData(data);
        send_color_query();
        send_height_query();
      });  
  } else {
    $.getJSON('/static/world_map_hd.json', {},
              function (data) {
        map.setMapData(data);
        send_color_query();
        send_height_query();
      });
  }
};


function toggle_help() {
  var help = $("#help-container");
  if (help.is(":visible")) {
    help.width(0);
    help.hide();
    $("#help-button").html("Show help");
  } else {
    help.width("20em");
    help.show();
    $("#help-button").html("Hide help");
  }
  on_resize();
  return false;
}

function on_resize() {
  var window_w = document.documentElement.clientWidth;
  var window_h = document.documentElement.clientHeight;
  
  var mapdiv = $("#mapdiv");
  var mapdiv_left = mapdiv.offset().left;
  var mapdiv_top = mapdiv.offset().top;
  
  var w = window_w - mapdiv_left - 5;
  var h = window_h - mapdiv_top - 5;
  
  var help = $("#help-container");
  var help_left = help.offset().left;
  
  if (help.is(":visible")) {
    w = help_left - mapdiv_left;
  }
  
  if (w < 600 || h < 350) {
    $("body").css("overflow", "scroll");
    if (w < 600) {
      w = Math.min(600, window_w - 10);
    }
    if (h < 350) {
      h = Math.min(350, window_h - 10);
    }
  } else {
    $("body").css("overflow", "hidden");
  }
  
  mapdiv.width(w + "px");
  mapdiv.height(h + "px");
  map.resize();
}

function pretty_number(number) {
    return number.toLocaleString("en-US");
}

function on_mouse_over(countryID, countryName) {
  var info = "<h4>" + countryName + "</h4>";

  if (height_data.values.hasOwnProperty(countryID)) {
    var height_value = height_data.values[countryID];
    info +=
    "<p>Height</p>" +
           "<ul><li>Dataset: " + height_data.name +
           "</li><li>Unit: " + height_data.unit +
           "</li><li>Value: " + pretty_number(height_value) +
           "</li><li>Time: " + height_data.times[countryID] +
           "</li></ul>";
  }
  
  if (color_data.values.hasOwnProperty(countryID)) {
    var color_value = color_data.values[countryID];
    info +=
    "<p>Color</p>" +
           "<ul><li>Dataset: " + color_data.name +
           "</li><li>Unit: " + color_data.unit +
           "</li><li>Value: " + pretty_number(color_value) +
           "</li><li>Time: " + color_data.times[countryID] +
           "</li></ul>"
  }
  
  return info;
}


function init_color_pickers() {
    var initValues = {
      showPaletteOnly: true,
      togglePaletteOnly: true,
      togglePaletteMoreText: 'more',
      togglePaletteLessText: 'less',
      color: "#ff0",
      change: update_map_colors,
      clickoutFiresChange: true,
      palette: [
        ["#000","#222222","#666","#999","#ccc","#eee","#f3f3f3","#fff"],
        ["#f00","#f90","#ff0","#0f0","#0ff","#00f","#90f","#f0f"],
        ["#ea9999","#f9cb9c","#ffe599","#b6d7a8","#a2c4c9","#9fc5e8","#b4a7d6","#d5a6bd"],
        ["#e06666","#f6b26b","#ffd966","#93c47d","#76a5af","#6fa8dc","#8e7cc3","#c27ba0"],
        ["#c00","#e69138","#f1c232","#6aa84f","#45818e","#335577","#674ea7","#a64d79"],
        ["#900","#b45f06","#bf9000","#38761d","#134f5c","#0b5394","#351c75","#741b47"],
        ["#600","#783f04","#7f6000","#274e13","#0c343d","#073763","#20124d","#4c1130"]
      ]
    };

    $("#minColor").spectrum(initValues);

    initValues.color = "#f00";
    $("#maxColor").spectrum(initValues);

    initValues.color = "#222222";
    initValues.change = update_map_dataless_countries_color;
    $("#NoDataColor").spectrum(initValues);

    initValues.color = "#335577";
    initValues.change = update_map_background_color;
    $("#BackgroundColor").spectrum(initValues);
}


$(document).ready(function () {
  map = new Map3D(document.getElementById("mapdiv"));
  map.setMouseOverHandler(on_mouse_over);
  load_map_model(false);
  
  init_color_pickers();
  
  //update_map_heights();
  update_map_colors();
  update_map_background_color();
  update_map_dataless_countries_color();
  on_resize();
  
  $("#color-select").change(send_color_query);
  $("#color-param-select").change(send_color_query);
  $("#height-select").change(send_height_query);
  $("#height-param-select").change(send_height_query);
  $('#slider').change(update_map_heights);
  
  $("#hide_countries").change(update_map_visibilities);
  $("#hd_map").change(function () {load_map_model($("#hd_map").is(":checked"))});
  $("#help-button").click(toggle_help);
  $(window).resize(on_resize);
});
