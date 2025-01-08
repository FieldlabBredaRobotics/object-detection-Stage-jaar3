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
      formatter: function (val: number) {
        return typeof val === 'number' ? val.toFixed(0) : val;
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
        formatter: function (val: number) {
          return typeof val === 'number' ? val.toFixed(0) : val;
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
      height: 350,
      stacked: true
    },
    title: {
      text: "Text Detection Stats"
    },
    plotOptions: {
      bar: {
        horizontal: false,
        dataLabels: {
          position: 'top'
        },
        barHeight: '75%'
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
      max: 20, // Default max value
      tickAmount: 8,
      labels: {
        formatter: function (val: number) {
          return typeof val === 'number' ? val.toFixed(0) : val;
        }
      }
    }
  };

  // Mapping van originele namen naar Nederlandse namen
  private nameMapping: { [key: string]: string } = {
    'carkeys': 'autosleutels',
    'auto sleutels': 'autosleutels',
    'car-key': 'autosleutels',
    'wallet': 'portemonnee',
    'comb': 'kam',
    'glasses': 'bril',
    'keys': 'sleutels',
    'mobile_phone': 'telefoon',
    'mobile-phone': 'telefoon',
    'pen': 'pen',
    'watch': 'horloge'
  };

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    // Haal de data op voor de eerste statistiek
    this.apiService.getObjectDetectionStats().subscribe((detectionStats: any[]) => {
      // Sorteer de data aflopend op basis van de count
      const sortedStats = detectionStats.sort((a, b) => b.count - a.count);
      const categories = sortedStats.map((stat: any) => stat.name);
      const data = sortedStats.map((stat: any) => ({
        x: this.nameMapping[stat.name] || stat.name,
        y: stat.count
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
          categories: categories.map(name => this.nameMapping[name] || name)
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
    });

    // Haal de data op voor de derde statistiek
    this.apiService.getTextStats().subscribe((textMatches: any[]) => {
      const groupedData = this.groupDataByClass(textMatches);
      const funnelData = this.generateFunnelChartData(groupedData);
      const maxCount = Math.max(
        ...funnelData.series[0].data,
        ...funnelData.series[1].data
      );

      this.funnelChartOptions = {
        ...this.funnelChartOptions,
        series: funnelData.series,
        xaxis: {
          categories: funnelData.categories.map((name: string | number) => this.nameMapping[name] || name)
        },
        yaxis: {
          ...this.funnelChartOptions.yaxis,
          max: Math.ceil(maxCount / 20) * 20
        }
      };
    });
  }

  groupDataByClass(stats: any[]): any {
    const groupedData: any = {};
    stats.forEach(stat => {
      if (stat.detected_product.toLowerCase() === 'niks herkend') {
        return;
      }
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
      const labels = Object.keys(correctProducts as { [key: string]: number }).map(name => this.nameMapping[name] || name);
      pieChartOptions.push({
        series: series,
        chart: {
          type: "pie",
          height: 240
        },
        labels: labels,
        title: {
          text: `Detection Breakdown for ${this.nameMapping[detectedProduct] || detectedProduct}`
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
      if (detectedProduct.toLowerCase() === 'niks herkend') {
        continue;
      }
      const correctProductsTyped = correctProducts as { [key: string]: number };
      const correctCount = correctProductsTyped[detectedProduct] || 0;
      const incorrectCount = Object.values(correctProductsTyped).reduce((acc: number, count: number) => acc + count, 0) - correctCount;
      funnelData.series[0].data.push(correctCount);
      funnelData.series[1].data.push(incorrectCount);
      funnelData.categories.push(this.nameMapping[detectedProduct] || detectedProduct);
    }
    return funnelData;
  }
}