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
  detectionRunning: boolean = false;
  detectedClasses: string[] = []; // Voeg deze regel toe

  constructor(private apiService: ApiService) {
    this.objectClasses.forEach(objectClass => {
      this.feedback[objectClass] = null;
      this.correctClass[objectClass] = '';
    });
  }

  startDetection() {
    this.apiService.startDetection().subscribe(response => {
      console.log(response);
      this.detectionRunning = true; // Zet de status op true
    });
  }

  stopDetection() {
    this.apiService.stopDetection().subscribe(response => {
      console.log(response);
      this.detectionRunning = false; // Zet de status op false
    });
  }

  processNaturalLanguage() {
    // Toon de pop-up direct
    const correct = confirm(`Heb ik het product "${this.userInput}" goed herkend?`);
    if (!correct) {
      const correctProduct = prompt('Wat is het juiste product?') || '';
      this.apiService.saveProductMatch(this.userInput, correctProduct).subscribe();
    }
  
    // Voer de objectdetectie en database-updates op de achtergrond uit
    this.apiService.captureAndDetect().subscribe(detectionResponse => {
      if (detectionResponse.status === 'success') {
        console.log('Detected objects:', detectionResponse.detected_objects);
        this.detectedClasses = Object.keys(detectionResponse.detected_objects); // Sla de gedetecteerde objecten op
        this.apiService.processNaturalLanguage(this.userInput).subscribe(response => {
          this.detectedObject = response.detected_object;
          if (response.status === 'success') {
            console.log(`Detected object: ${this.detectedObject}`);
          }
        });
      } else {
        console.error('Error capturing and detecting objects:', detectionResponse.message);
      }
    });
  }

  giveFeedback(objectClass: string, isCorrect: boolean) {
    this.feedback[objectClass] = isCorrect;
    if (isCorrect) {
      alert('Dankjewel voor je feedback!');
      this.detectedClasses = this.detectedClasses.filter(cls => cls !== objectClass); // Verwijder het object uit de feedback container
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
    this.apiService.saveProductMatch(this.userInput, correctProduct).subscribe(() => {
      alert('Dankjewel voor je feedback!');
      this.feedback[objectClass] = null;
      this.detectedClasses = this.detectedClasses.filter(cls => cls !== objectClass); // Verwijder het object uit de feedback container
    });
  }
}