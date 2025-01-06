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
  ApexTooltip,
  ApexNonAxisChartSeries
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
          return typeof val === 'number' ? val.toFixed(0) : val;
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val: number, opts: any) {
        const confidence = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].confidence;
        return typeof val === 'number' ? `${val.toFixed(0)} (${confidence}%)` : val;
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
          return typeof val === 'number' ? `${val.toFixed(0)} (Confidence: ${confidence}%)` : val;
        }
      }
    }
  };

  pieChartOptions: any[] = [];
  funnelChartOptions: {
    series: ApexAxisChartSeries;
    chart: ApexChart;
    title: ApexTitleSubtitle;
    plotOptions: ApexPlotOptions;
    dataLabels: ApexDataLabels;
    xaxis: ApexXAxis;
    yaxis: ApexYAxis;
  } = {
    series: [],
    chart: {
      type: "bar",
      height: 350
    },
    title: {
      text: "Object Detection Funnel"
    },
    plotOptions: {
      bar: {
        horizontal: true,
        barHeight: '75%',
        dataLabels: {
          position: 'top'
        }
      }
    },
    dataLabels: {
      enabled: true
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
          return typeof val === 'number' ? val.toFixed(0) : val;
        }
      }
    }
  };

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    // Haal de data op voor de eerste statistiek
    this.apiService.getObjectDetectionStats().subscribe((detectionStats: any[]) => {
      const categories = detectionStats.map((stat: any) => stat.name);
      const data = detectionStats.map((stat: any) => ({
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

    // Haal de data op voor de tweede statistiek
    this.apiService.getProductStats().subscribe((productStats: any[]) => {
      const groupedData = this.groupDataByClass(productStats);
      this.pieChartOptions = this.generatePieChartOptions(groupedData);

      // Haal de data op voor de trechterdiagram
      const funnelData = this.generateFunnelChartData(groupedData);
      this.funnelChartOptions = {
        ...this.funnelChartOptions,
        series: funnelData.series,
        xaxis: {
          categories: funnelData.categories
        }
      };
    });
  }

  groupDataByClass(stats: any[]): any {
    const groupedData: any = {};
    stats.forEach(stat => {
      if (!groupedData[stat.detected_product]) {
        groupedData[stat.detected_product] = {};
      }
      if (!groupedData[stat.detected_product][stat.correct_product]) {
        groupedData[stat.detected_product][stat.correct_product] = 0;
      }
      groupedData[stat.detected_product][stat.correct_product]++;
    });
    return groupedData;
  }

  generatePieChartOptions(groupedData: any): any[] {
    const pieChartOptions: any[] = [];
    for (const [detectedProduct, correctProducts] of Object.entries(groupedData)) {
      const series = Object.values(correctProducts as { [key: string]: number });
      const labels = Object.keys(correctProducts as { [key: string]: number });
      pieChartOptions.push({
        series: series,
        chart: {
          type: "pie",
          height: 350
        },
        labels: labels,
        title: {
          text: `Detection Breakdown for ${detectedProduct}`
        },
        dataLabels: {
          enabled: true
        }
      });
    }
    return pieChartOptions;
  }

  generateFunnelChartData(groupedData: any): any {
    const funnelData: any = {
      series: [
        {
          name: 'Correct',
          data: []
        },
        {
          name: 'Incorrect',
          data: []
        }
      ],
      categories: []
    };
    for (const [detectedProduct, correctProducts] of Object.entries(groupedData)) {
      const correctProductsTyped = correctProducts as { [key: string]: number };
      const correctCount = correctProductsTyped[detectedProduct] || 0;
      const incorrectCount = Object.values(correctProductsTyped).reduce((acc: number, count: number) => acc + count, 0) - correctCount;
      funnelData.series[0].data.push(correctCount);
      funnelData.series[1].data.push(incorrectCount);
      funnelData.categories.push(detectedProduct);
    }
    return funnelData;
  }
}