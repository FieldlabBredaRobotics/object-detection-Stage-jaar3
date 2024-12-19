import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexYAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexPlotOptions,
  NgApexchartsModule,
  ApexTooltip
} from "ng-apexcharts";

@Component({
  selector: 'app-product-stats',
  templateUrl: './product-stats.component.html',
  styleUrls: ['./product-stats.component.css'],
  imports: [CommonModule, NgApexchartsModule],
  standalone: true,
})
export class ProductStatsComponent implements OnInit {
  chartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    xaxis: ApexXAxis;
    yaxis: ApexYAxis;
    dataLabels: ApexDataLabels;
    title: ApexTitleSubtitle;
    plotOptions: ApexPlotOptions;
    tooltip: ApexTooltip;
  } = {
    series: [],
    chart: {
      type: "bar",
      height: 350
    },
    xaxis: {
      categories: []
    },
    yaxis: {
      min: 0,
      max: 160,
      tickAmount: 8,
      labels: {
        formatter: function (val: number) {
          return val.toFixed(0);
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val: number, opts: any) {
        const confidence = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].confidence;
        return `${val.toFixed(0)} (${confidence}%)`;
      },
      style: {
        colors: ['#000']
      }
    },
    title: {
      text: "Object Detection Stats"
    },
    plotOptions: {
      bar: {
        distributed: true,
        dataLabels: {
          position: 'top'
        },
        colors: {
          ranges: [
            {
              from: 0,
              to: 100,
              color: '#29a7a8'
            },
            {
              from: 101,
              to: 200,
              color: '#ff4560'
            }
          ]
        }
      }
    },
    tooltip: {
      y: {
        formatter: function (val: number, opts: any) {
          const confidence = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].confidence;
          return `${val.toFixed(0)} (Confidence: ${confidence}%)`;
        }
      }
    }
  };

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getObjectDetectionStats().subscribe((stats: any[]) => {
      const categories = stats.map((stat: any) => stat.name);
      const data = stats.map((stat: any) => ({
        x: stat.name,
        y: stat.count,
        confidence: stat.confidence
      }));

      this.chartOptions = {
        ...this.chartOptions,
        series: [
          {
            name: "Object Detection Count",
            data: data
          }
        ],
        xaxis: {
          categories: categories
        },
        yaxis: {
          ...this.chartOptions.yaxis,
          max: Math.ceil(Math.max(...data.map(d => d.y)) / 20) * 20
        }
      };
    });
  }
}