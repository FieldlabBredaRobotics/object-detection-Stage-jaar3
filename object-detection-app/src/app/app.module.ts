import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
// import { AppRoutingModule } from './app-routing.module';  // Zorg ervoor dat dit goed is geïmporteerd
import { AppComponent } from './app.component';
import { ObjectDetectionComponent } from './object-detection/object-detection.component';
import { ProductStatsComponent } from './product-stats/product-stats.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgChartsModule } from 'ng2-charts';
import { RouterModule } from '@angular/router'; // Dit is nodig, maar geen routes hier configureren
import { AppRoutesModule } from './app.routes';
import { StartScreenComponent } from './start-screen/start-screen.component';

@NgModule({
  declarations: [
  //  AppComponent,
    StartScreenComponent,
    ObjectDetectionComponent,
    ProductStatsComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    NgChartsModule,
    BrowserModule,
    AppRoutesModule, 
    RouterModule,
   AppRoutesModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
