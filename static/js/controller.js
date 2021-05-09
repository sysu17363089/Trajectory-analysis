$(document).ready(function(){
    $(function () { $(".popover-options a").popover({html : true });});
    let convertData = function (data) {
        var res = [];
        for (var i = 0; i < data.length; i++) {
            res.push({
                name: "name",
                value: data[i].concat(100)
            });
        }
        return res;
    };

    let convertPOIData = function (coor, interest,name) {
        const res = [];
        res.push({
            name: name,
            value: coor.concat(interest)
        });
        return res;
    };

    let random_color = function() {
        let colorArr = ['0','2','4','6', '8', '9', 'A', 'C', 'E']
        let color = ""
        for(let i = 0; i < 6; i++) {
            color += colorArr[Math.floor((Math.random() * (colorArr.length)))]
        }
        return "#" + color
    }

    let cleanup_series = function(){
        myChart.clear();
        option.series.length = 0;
        option.legend = {};
        option.tooltip = {};
    }


    let draw_circle = function(center, radius, color, name, data){
        option.tooltip = {//鼠标放上去提示
            // 鼠标是否可以进入悬浮框
            enterable: true,
            triggerOn: 'mousemove',
            trigger: 'item',
            // 浮层隐藏的延迟
            hideDelay: 800,
            // 背景色
             appendToBody: true,
            backgroundColor: 'rgba(0,0,0,0.5)',
            formatter: function (params) {
               return `
                <div class=title>停留点数量：40</div>
                <div class=title>兴趣度：${params.value[2].toFixed(4)}</div>
                    `
            }
        },
        //
        option.series.push({
            type: 'scatter',
            coordinateSystem: 'bmap',
            name: name,
            data: convertPOIData(center, data, name),
            symbol: "circle",
            symbolSize: radius / 2.0,
            symbolSize: 50,
            itemStyle: {
                normal: {
                    color: color,
                    opacity: 0.7,
                },
            },
        })

    }
    
    let draw_points = function(points, point_color, series_name){
        let scatter_color = point_color == undefined ? "purple" : point_color
        option.series.push({
            type: 'scatter',
            name: series_name,
            coordinateSystem: 'bmap',
            data: convertData(points),
            symbol: "circle",
            symbolSize: 5,
            itemStyle: {
                normal: {
                    color: scatter_color
                },
            }
        })
    }

    let draw_semantic_points = function(lon, lat, point_color, series_name){
        let scatter_color = point_color == undefined ? "purple" : point_color
        option.tooltip = {//鼠标放上去提示
            // 鼠标是否可以进入悬浮框
            enterable: true,
            triggerOn: 'mousemove',
            trigger: 'item',
            // 浮层隐藏的延迟
            hideDelay: 800,
            // 背景色
             appendToBody: true,
            backgroundColor: 'rgba(0,0,0,0.5)',
            formatter: function (params) {
               return `
                <div class=title>区域类型：${params.name}</div>
                <div class=title>停留起始时间：2008-12-10 09:21:00 </div>
                <div class="title">停留结束时间：2008-12-10 18:37:55</div>
                 `
            }
        },
        option.series.push({
            type: 'scatter',
            name: series_name,
            coordinateSystem: 'bmap',
            data: [{name:series_name, value:[lon, lat, 100]}],
            symbol: "circle",
            symbolSize: 35,
            label: {
                normal: {
                    formatter: function (data) {
                        return data.name
                    },
                    position: 'inside',
                    show: true,
                    textStyle: {
                        color: '#000',
                        fontSize: 12,
                        font_weight: 400,
                    },
                }
            },
            itemStyle: {
                normal: {
                    color: scatter_color
                },
            },
        })
    }
    
    let draw_lines = function(lines, line_color, series_name, width=1.0, opacity=0.6){
        let polyline_color = line_color == undefined ? "purple" : line_color
        let trajs = []
        for(let i = 0; i<lines.length; i++){
            trajs.push({coords: lines[i]})
        }
        option.series.push({
            name: series_name,
            type: 'lines',
            coordinateSystem: 'bmap',
            polyline: true,
            silent: true,
            data: trajs,
            lineStyle: {
                normal: {
                    color: polyline_color,
                    opacity: opacity,
                    width: width
                }
            },
            progressiveThreshold: 500,
            progressive: 200})

    }

    let refresh_series = function(lines, points, center, line_color, point_color, series_name) {
        // draw_points(points, point_color, series_name + 'p')
        draw_lines(lines, line_color, series_name)
        
        if(center != undefined){
            option.bmap.center = center
        }
    }

    $("#confirm").click(function(){
        $.ajax({
            url: '/get_files',
            type: 'get',
            data: {},
            dataType: "json",
            success: function(data){
                cleanup_series()
                refresh_series(data.lines, data.points, data.center)
                setTimeout(myChart.setOption(option), 500)
            }, error: function() {
                alert("error");
            }
        })
    })




    $("#toSemantic").click(function(){
    $.ajax({
        url: '/to_semantic',
        type: 'get',
        data: {},
        dataType: "json",
        success: function(data){
            cleanup_series()
            let semantic_traj = data['semantic_traj']
            for(let traj of semantic_traj){
                let line = []
                let color = random_color()
                for(let iter of traj) {
                    line.push([iter['Longitude'], iter['Latitude']])
                    draw_semantic_points(iter['Longitude'], iter['Latitude'], color, iter['type'])
                }
                draw_lines([line], color, 'none', 2.0, 1.0)
            }
            console.log(option)
            setTimeout(myChart.setOption(option), 500)
        }, error: function(){
            alert("error");
        }
    })})

    $("#traj_cluster").click(function(){
    $.ajax({
        url: '/traj_cluster',
        type: 'get',
        data: {},
        dataType: "json",
        success: function(data){
            cleanup_series()
            let names = []
            for(let i = 0; i < data['cluster'].length; i++ ){
                let name = "cluster" + (i+1).toString();
                let color = random_color()
                draw_lines(data['cluster'][i], color, name)
                for(let j = 0; j < data['cluster'][i].length; j++){
                    draw_points(data['cluster'][i][j], color)
                }
                names.push(name)
            }
            option.legend = {
                left: 20,
                top: 20,
                data: names,
                textStyle: {
                    fontSize: 18
                }
            }
            setTimeout(myChart.setOption(option), 500)
        }, error: function(){
            alert("error");
        }
    })})

    $("#stop_points").click(function(){
    $.ajax({
        url: '/get_stop_points',
        type: 'get',
        data: {},
        dataType: "json",
        success: function(data){
            cleanup_series()
            let stop_points = data['stop_points']
            // let color = random_color()
            draw_points(stop_points, 'black')
            setTimeout(myChart.setOption(option), 500)
        }, error: function(){
            alert("error");
        }
    })})

    $("#POI").click(function(){
    $.ajax({
        url: '/generate_POI',
        type: 'get',
        data: {},
        dataType: "json",
        success: function(data){
            cleanup_series()
            let names = []
            let clusters = data['cluster']
            let radius = data['radius']
            let centers = data['centers']
            let interest = data['interest']
            let i = 0;
            for(let key in clusters) {
                let name = "cluster" + key;
                names.push(name);
                let color = random_color()
                draw_points(clusters[key], color, name)
                draw_circle(centers[i], radius[i], color, key, interest[key])
                i++
            }
            option.legend = {
                left: 20,
                top: 20,
                data: names,
                textStyle: {
                    fontSize: 18
                }
            }
            setTimeout(myChart.setOption(option), 500)
        }, error: function(){
            alert("error");
        }
    })})

    const myChart = echarts.init(document.getElementById('right'));
    // 指定图表的配置项和数据
    var option = {
        backgroundColor: 'black',

        bmap: {
            center: [116.395577, 39.892257],
            zoom: 14.3,
            roam: true,
            mapStyle: {
                styleJson:   [{
                    'featureType': 'water',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'land',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#f3f3f3'
                    }
                }, {
                    'featureType': 'railway',
                    'elementType': 'all',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'highway',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#fdfdfd'
                    }
                }, {
                    'featureType': 'highway',
                    'elementType': 'labels',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'geometry',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'geometry.fill',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'poi',
                    'elementType': 'all',

                }, {
                    'featureType': 'green',
                    'elementType': 'all',
                }, {
                    'featureType': 'subway',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'manmade',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'local',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'labels',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'boundary',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'building',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'label',
                    'elementType': 'labels.text.fill',
                    'stylers': {
                        'color': '#999999'
                    }
                }]
            }
         },
        series: []
    };

    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
})

