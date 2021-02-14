var markers = [];
var markers2 = [];
var circles = [];
var infoWindows = [];
var infoWindows2 = [];
var markerData = data.markerData;
var markerData2 = data.markerData2;
console.log(markerData);
function initMap() {
  jQuery(function($){
    var map, map_center;
    //初期のズーム レベル（指定がなければ 16）
    var zoom = 12;
    //マーカーのタイトル
    var title = $('#venue').text();
 
    //マップ生成のオプション
    //center は Geolocation から取得して後で設定
    var opts = {
      zoom: zoom,
      mapTypeId: "roadmap",  //初期マップ タイプ  
      scaleControl: true
    };
 
    //マップのインスタンスを生成
    map = new google.maps.Map(document.getElementById("map_canvas"), opts);
 
    //ジオコーディングのインスタンスの生成
    var geocoder = new google.maps.Geocoder();
 
    var address = $('#address').text();
    var my_reg = /〒\s?\d{3}(-|ー)\d{4}/;
    //郵便番号を含めるとおかしくなる場合があったので、郵便番号は削除
    address = address.replace(my_reg, '');
 
    //geocoder.geocode() にアドレスを渡して、コールバック関数を記述して処理
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status === 'OK' && results[0]) {
        //results[0].geometry.location に緯度・経度のオブジェクトが入っている
        map_center = results[0].geometry.location;
        //地図の中心位置を設定
        map.setCenter(map_center);
        //マーカーのインスタンスを生成
        var marker = new google.maps.Marker({
        //マーカーを配置する Map オブジェクトを指定
        map: map,
        //マーカーの初期の場所を示す LatLng を指定  
        position: map_center,  
        //マーカーをアニメーションで表示
        // animation: google.maps.Animation.DROP,  
        title: title,
        icon: {
            fillColor: "#000",                //塗り潰し色
            fillOpacity: 0.8,                    //塗り潰し透過率
            path: google.maps.SymbolPath.CIRCLE, //円を指定
            scale: 1.5,                           //円のサイズ
            strokeColor: "#000",              //枠の色
            strokeWeight: 1.0                    //枠の透過率
        }
        });

  // マーカー毎の処理
 for (var i = 0; i < markerData.length; i++) {
        if (markerData[i]['color'] == 0){
            // 過剰
            var circle_color = '#ff0000';
            var msg = '<p style="color:#ff0000;">車両台数が過剰です</p>'
            var link = '<a href="../deletesetting/' + markerData[i]['id'] +'" class="btn smbtn">配車を変更する</a>'
        }else if (markerData[i]['color'] == 1){
            // 不足
            var circle_color = '#005FFF';
            var msg = '<p style="color:#005FFF;">車両台数が不足しています!!</p>'
            var link = '<a href="../createsetting/' + markerData[i]['id'] +'" class="btn smbtn">車両を配置する</a>'
        }else{
            // 適正
            var circle_color = '#00CC99';
            var msg = '<p style="color:#00CC99;">車両台数は適正です</p>'
            var link = ''
        }
        markerLatLngs = new google.maps.LatLng({lat: Number(markerData[i]['lat']), lng: Number(markerData[i]['lng'])}); // 緯度経度のデータ作成        
        markers[i] = new google.maps.Marker({ // マーカーの追加
            position: markerLatLngs, // マーカーを立てる位置を指定
            map: map, // マーカーを立てる地図を指定
            icon: {
                path: 'M -8,-8 8,8 M 8,-8 -8,8',     //座標（×）
                strokeColor: "#FFF",              //線の色
                strokeWeight: 1.0                    //線の太さ
            }
        });
        circles[i] = new google.maps.Circle({
            center: markerLatLngs,       // 中心点(google.maps.LatLng)
            fillColor: circle_color,   // 塗りつぶし色
            fillOpacity: 0.5,       // 塗りつぶし透過度（0: 透明 ⇔ 1:不透明）
            map: map,             // 表示させる地図（google.maps.Map）
            radius: 3000,          // 半径（ｍ）
            strokeColor: circle_color, // 外周色
            strokeOpacity: 1,       // 外周透過度（0: 透明 ⇔ 1:不透明）
            strokeWeight: 1         // 外周太さ（ピクセル）
        });

        infoWindows[i] = new google.maps.InfoWindow({ // 吹き出しの追加
          content: '<div class="sample"><h6>エリア' + markerData[i]['id'] + '</h6>' + markerData[i]['address'] + msg + link + '</div>' // 吹き出しに表示する内容
        });
 
     markerEvent(i); // マーカーにクリックイベントを追加
 }
        // マーカーにクリックイベントを追加
        function markerEvent(i) {
            markers[i].addListener('click', function() { // マーカーをクリックしたとき
            infoWindows[i].open(map, markers[i]); // 吹き出しの表示
        });
        }

for (var i = 0; i < markerData2.length; i++) {
    markerLatLngs2 = new google.maps.LatLng({lat: Number(markerData2[i]['lat']), lng: Number(markerData2[i]['lng'])}); // 緯度経度のデータ作成        
    markers2[i] = new google.maps.Marker({ // マーカーの追加
        position: markerLatLngs2, // マーカーを立てる位置を指定
        map: map, // マーカーを立てる地図を指定
        animation: google.maps.Animation.DROP
    });

    infoWindows2[i] = new google.maps.InfoWindow({ // 吹き出しの追加
        content: '<div class="sample"><h6>駐車場'+ markerData2[i]['id'] + '</h6>' + markerData2[i]['address'] + '</div>' // 吹き出しに表示する内容
    });
 
    markerEvent2(i); // マーカーにクリックイベントを追加
}
    // マーカーにクリックイベントを追加
    function markerEvent2(i) {
        markers2[i].addListener('click', function() { // マーカーをクリックしたとき
            infoWindows2[i].open(map, markers2[i]); // 吹き出しの表示
        });
    }

        //情報ウィンドウに表示するコンテンツを作成
        //urlが指定してあればリンクつきのタイトルと住所を表示（URLがない場合もあるため）
        var url = $("#url a").attr('href');
        var content;
        if (url) {
          content = '<div id="map_content"><p><a href="' + url + '" target="_blank"> ' + title + '</a><br />' + address + '</p></div>';
        }else {
          //urlが指定してなければ、リンクなしのタイトルと住所を表示
          content = '<div id="map_content"><p>' + title + '<br />' + address + '</p></div>';
        }
 
        //情報ウィンドウのインスタンスを生成
        var infowindow = new google.maps.InfoWindow({
          content: content,
        });
 
        //marker をクリックすると情報ウィンドウを表示(リスナーの登録）
        google.maps.event.addListener(marker, 'click', function() {
          //第2引数にマーカーを指定して紐付け
          infowindow.open(map, marker);
        });
      } else {
        alert("住所から位置の取得ができませんでした。: " + status);
      }
    });
  }); 
}