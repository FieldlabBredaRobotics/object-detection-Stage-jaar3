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
  imports: [HttpClientModule, CommonModule, FormsModule],
  standalone: true,
})
export class ObjectDetectionComponent {
  detectedObject: string = '';
  userInput: string = '';
  cameraFeedUrl: string = 'http://localhost:5000/video_feed';
  objectClasses: string[] = ['Telefoon', 'Portemonnee', 'Pen', 'Kam', 'Horloge', 'Sleutels', 'Bril', 'Auto Sleutels'];
  feedback: { [key: string]: boolean | null } = {};
  correctClass: { [key: string]: string } = {};

  constructor(private apiService: ApiService) {
    this.objectClasses.forEach(objectClass => {
      this.feedback[objectClass] = null;
      this.correctClass[objectClass] = '';
    });
  }

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
        const correct = confirm(`Heb je het product "${this.detectedObject}" goed herkend?`);
        if (!correct) {
          const correctProduct = prompt('Wat is het juiste product?') || '';
          this.apiService.saveProductMatch(this.userInput, this.detectedObject, correctProduct).subscribe();          
        }
      }
    });
  }

  giveFeedback(objectClass: string, isCorrect: boolean) {
    this.feedback[objectClass] = isCorrect;
    if (isCorrect) {
      alert('Dankjewel voor je feedback!');
    }
  }

  showDropdown(objectClass: string) {
    this.objectClasses.forEach(cls => {
      if (cls !== objectClass) {
        this.feedback[cls] = null;
      }
    });
    this.feedback[objectClass] = false;
  }

  submitFeedback(objectClass: string) {
    const correctProduct = this.correctClass[objectClass];
    this.apiService.saveProductMatch(this.userInput, objectClass, correctProduct).subscribe(() => {
      alert('Dankjewel voor je feedback!');
      this.feedback[objectClass] = null;
    });
  }
}