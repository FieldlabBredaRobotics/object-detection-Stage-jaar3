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
  detectedClasses: string[] = [];
  showFeedbackSection: boolean = false;
  displayStyle = "none";
  showDropdown: boolean = false;
  selectedClass: string = '';

  constructor(private apiService: ApiService) {
    this.objectClasses.forEach(objectClass => {
      this.feedback[objectClass] = null;
      this.correctClass[objectClass] = '';
    });
  }

  openPopup() { 
    this.displayStyle = "block"; 
  } 
  closePopup() { 
    this.displayStyle = "none"; 
    this.showDropdown = false;
  } 

  startDetection() {
    this.apiService.startDetection().subscribe(response => {
      console.log(response);
      this.detectionRunning = true;
    });
  }

  stopDetection() {
    this.apiService.stopDetection().subscribe(response => {
      console.log(response);
      this.detectionRunning = false;
    });
  }

  processNaturalLanguage() {
    this.apiService.captureAndDetect().subscribe(detectionResponse => {
      if (detectionResponse.status === 'success') {
        console.log('Detected objects:', detectionResponse.detected_objects);
        this.detectedClasses = Object.keys(detectionResponse.detected_objects);
        this.showFeedbackSection = true;
        this.apiService.processNaturalLanguage(this.userInput).subscribe(response => {
          this.detectedObject = response.detected_object;
          if (response.status === 'success') {
            this.openPopup();
          }
        });
      } else {
        console.error('Error capturing and detecting objects:', detectionResponse.message);
      }
    });
  }

  handleFeedback(isCorrect: boolean) {
    if (isCorrect) {
      this.apiService.saveTextMatch(this.detectedObject, this.detectedObject).subscribe();
      this.closePopup();
    } else {
      this.showDropdown = true;
    }
  }

  submitFeedback() {
    this.apiService.saveTextMatch(this.detectedObject, this.selectedClass).subscribe(() => {
      this.closePopup();
    });
  }

  giveFeedback(objectClass: string, isCorrect: boolean) {
    this.feedback[objectClass] = isCorrect;
    if (isCorrect) {
      alert('Dankjewel voor je feedback!');
      this.apiService.saveProductMatch(objectClass, objectClass).subscribe(() => {
        this.detectedClasses = this.detectedClasses.filter(cls => cls !== objectClass);
      });
    } else {
      this.showDropdown = true;
    }
  }
}