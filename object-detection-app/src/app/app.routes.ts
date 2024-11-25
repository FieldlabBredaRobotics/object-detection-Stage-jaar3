// import { NgModule } from '@angular/core';
// import { RouterModule, Routes } from '@angular/router';
// import { AppComponent } from './app.component';
// import { ObjectDetectionComponent } from './object-detection/object-detection.component';
// import { ProductStatsComponent } from './product-stats/product-stats.component';

// export const routes: Routes = [
//   { path: '', component: AppComponent },
//   { path: 'product-stats', component: ProductStatsComponent },
//   { path: 'object-detection', component: ObjectDetectionComponent }
// ];

// @NgModule({
//   imports: [RouterModule.forRoot(routes)],
//   exports: [RouterModule]
// })
// export class AppRoutesModule { }

import { RouterModule, Routes } from '@angular/router';
import { ObjectDetectionComponent } from './object-detection/object-detection.component';
import { ProductStatsComponent } from './product-stats/product-stats.component';
import { AppComponent } from './app.component';
import { NgModule } from '@angular/core';
import { StartScreenComponent } from './start-screen/start-screen.component';

export const routes: Routes = [
  { path: '', component: StartScreenComponent },
  { path: 'product-stats', component: ProductStatsComponent },
  { path: 'object-detection', component: ObjectDetectionComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutesModule { }