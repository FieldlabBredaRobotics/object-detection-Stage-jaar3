// import { Component } from '@angular/core';
// import { ApiService } from '../api.service';

// @Component({
//   selector: 'app-object-detection',
//   templateUrl: './object-detection.component.html',
//   styleUrls: ['./object-detection.component.css']
// })
// export class ObjectDetectionComponent {
//   detectedObject: string = '';
//   userInput: string = '';

//   constructor(private apiService: ApiService) {}

//   startDetection() {
//     this.apiService.startDetection().subscribe(response => {
//       console.log(response);
//     });
//   }

//   stopDetection() {
//     this.apiService.stopDetection().subscribe(response => {
//       console.log(response);
//     });
//   }

//   processNaturalLanguage() {
//     this.apiService.processNaturalLanguage(this.userInput).subscribe(response => {
//       this.detectedObject = response.detected_object;
//       if (response.status === 'success') {
//         // Vraag de gebruiker om te bevestigen of de AI het product correct herkend heeft
//         const correct = confirm(`Heb je het product "${this.detectedObject}" goed herkend?`);
//         if (!correct) {
//           const correctProduct = prompt('Wat is het juiste product?') || '';
//           this.apiService.saveProductMatch(this.userInput, this.detectedObject, correctProduct).subscribe();          
//         }
//       }
//     });
//   }
// }

// import { Component } from '@angular/core';

// @Component({
//   selector: 'app-object-detection',
//   imports: [],
//   templateUrl: './object-detection.component.html',
//   styleUrl: './object-detection.component.css'
// })
// export class ObjectDetectionComponent {

// }


import { Component } from '@angular/core';
import { ApiService } from '../api.service';
import { RouterOutlet } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-object-detection',
  templateUrl: './object-detection.component.html',
  styleUrls: ['./object-detection.component.css'],
  imports: [HttpClientModule, CommonModule,FormsModule ],
  standalone: true,
  
  
})
export class ObjectDetectionComponent {
  detectedObject: string = '';
  userInput: string = '';

  constructor(private apiService: ApiService) {}

  startDetection() {
    this.apiService.startDetection().subscribe(response => {
      console.log(response);
    });
  }

  stopDetection() {
    this.apiService.stopDetection().subscribe(response => {
      console.log(response);
    });
  }

  processNaturalLanguage() {
    this.apiService.processNaturalLanguage(this.userInput).subscribe(response => {
      this.detectedObject = response.detected_object;
      if (response.status === 'success') {
        // Vraag de gebruiker om te bevestigen of de AI het product correct herkend heeft
        const correct = confirm(`Heb je het product "${this.detectedObject}" goed herkend?`);
        if (!correct) {
          const correctProduct = prompt('Wat is het juiste product?') || '';
          this.apiService.saveProductMatch(this.userInput, this.detectedObject, correctProduct).subscribe();          
        }
      }
    });
  }
}
