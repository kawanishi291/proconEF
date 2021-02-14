(function() {
    'use strict';

      // パッケージのロード
      google.charts.load('current', {packages: ['corechart']});
      // コールバックの登録
      google.charts.setOnLoadCallback(drawChart);

      // コールバック関数の実装
      function drawChart() {
          // データの準備
          var data　= new google.visualization.DataTable();
          data.addColumn('string', 'Love');
          data.addColumn('number', 'Votes');
          data.addRow(['乗り心地がいい', 10]);
          data.addRow(['荷室の使いやすさ', 4]);
          data.addRow(['燃費の良さ', 9]);
          data.addRow(['排気量の少なさ', 4]);
          data.addRow(['車内空間が広い', 4]);
          data.addRow(['静かに走る', 3]);
          data.addRow(['馬力がある', 4]);
          data.addRow(['乗車定員が多い', 3]);
          data.addRow(['小回りが利く', 8]);
          data.addRow(['乗車しやすい', 7]);
          data.addRow(['安全性能が高い', 9]);
          data.addRow(['走行性能が高い', 6]);
          data.addRow(['車両サイズが小さい', 6]);

          // オプションの準備
          var options = {
              title: '利用者アンケート',
              width: 1200,
              height: 600,
              is3D: true
          };

          // 描画用インスタンスの生成および描画メソッドの呼び出し
          var chart = new google.visualization.PieChart(document.getElementById('target'));
          chart.draw(data, options);
      }


  })();