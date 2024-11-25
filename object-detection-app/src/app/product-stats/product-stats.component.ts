import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-product-stats',
  templateUrl: './product-stats.component.html',
  styleUrls: ['./product-stats.component.css']
})
export class ProductStatsComponent implements OnInit {
  stats: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getProductStats().subscribe(stats => {
      this.stats = stats;
    });
  }
}
