import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../api.service';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  NgApexchartsModule
} from "ng-apexcharts";

@Component({
  selector: 'app-product-stats',
  templateUrl: './product-stats.component.html',
  styleUrls: ['./product-stats.component.css'],
  imports: [CommonModule, NgApexchartsModule],
  standalone: true,
})
export class ProductStatsComponent implements OnInit {
  objectDetectionChartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    xaxis: ApexXAxis;
    dataLabels: ApexDataLabels;
    title: ApexTitleSubtitle;
  } = {
    series: [],
    chart: {
      type: "bar",
      height: 350
    },
    xaxis: {
      categories: []
    },
    dataLabels: {
      enabled: true
    },
    title: {
      text: "Object Detection Count"
    }
  };

  productDetectionAccuracyChartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    xaxis: ApexXAxis;
    dataLabels: ApexDataLabels;
    title: ApexTitleSubtitle;
  } = {
    series: [],
    chart: {
      type: "bar",
      height: 350
    },
    xaxis: {
      categories: []
    },
    dataLabels: {
      enabled: true
    },
    title: {
      text: "Product Detection Accuracy"
    }
  };

  textDetectionAccuracyChartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    xaxis: ApexXAxis;
    dataLabels: ApexDataLabels;
    title: ApexTitleSubtitle;
  } = {
    series: [],
    chart: {
      type: "bar",
      height: 350
    },
    xaxis: {
      categories: []
    },
    dataLabels: {
      enabled: true
    },
    title: {
      text: "Text Detection Accuracy"
    }
  };

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getObjectDetectionStats().subscribe(stats => {
      const categories = Object.keys(stats);
      const data = Object.values(stats) as number[];
      this.objectDetectionChartOptions = {
        ...this.objectDetectionChartOptions,
        series: [
          {
            name: "Object Detection Count",
            data: data
          }
        ],
        xaxis: {
          categories: categories
        }
      };
    });

    this.apiService.getProductDetectionAccuracy().subscribe(stats => {
      const categories = Object.keys(stats);
      const data = Object.values(stats) as number[];
      this.productDetectionAccuracyChartOptions = {
        ...this.productDetectionAccuracyChartOptions,
        series: [
          {
            name: "Product Detection Accuracy",
            data: data
          }
        ],
        xaxis: {
          categories: categories
        }
      };
    });

    this.apiService.getTextDetectionAccuracy().subscribe(stats => {
      const categories = Object.keys(stats);
      const data = Object.values(stats) as number[];
      this.textDetectionAccuracyChartOptions = {
        ...this.textDetectionAccuracyChartOptions,
        series: [
          {
            name: "Text Detection Accuracy",
            data: data
          }
        ],
        xaxis: {
          categories: categories
        }
      };
    });
  }
}