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
  detectionRunning: boolean = false;
  detectedClasses: string[] = [];
  showFeedbackSection: boolean = false;
  displayStyle = "none";
  showDropdown: boolean = false;
  selectedClass: string = '';
  showDropdownFor: { [key: string]: boolean } = {};
  correctClass: { [key: string]: string } = {};

  constructor(private apiService: ApiService) {
    this.objectClasses.forEach(objectClass => {
      this.showDropdownFor[objectClass] = false;
      this.correctClass[objectClass] = '';
    });
  }

  openPopup() { 
    this.displayStyle = "block"; 
    this.showDropdown = false;
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
            this.apiService.setTarget(this.detectedObject).subscribe(() => {
              this.openPopup();
            });
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
    if (this.selectedClass) {
      this.apiService.saveTextMatch(this.detectedObject, this.selectedClass).subscribe(() => {
        this.detectedObject = this.selectedClass; 
        this.apiService.setTarget(this.selectedClass).subscribe(() => {
          this.closePopup();
        });
      });
    } else {
      alert('Selecteer een juiste productklasse.');
    }
  }

  giveFeedback(objectClass: string, isCorrect: boolean) {
    if (isCorrect) {
      alert('Dankjewel voor je feedback!');
      this.apiService.saveProductMatch(objectClass, objectClass).subscribe(() => {
        this.detectedClasses = this.detectedClasses.filter(cls => cls !== objectClass);
        this.updateFeedbackSectionVisibility();
      });
    } else {
      this.showDropdownFor[objectClass] = true;
    }
  }

  submitFeedbackForObject(objectClass: string, selectedClass: string) {
    if (selectedClass) {
      this.apiService.saveProductMatch(objectClass, selectedClass).subscribe(() => {
        this.detectedClasses = this.detectedClasses.filter(cls => cls !== objectClass);
        this.updateFeedbackSectionVisibility();
      });
    } else {
      alert('Selecteer een juiste productklasse.');
    }
  }

  updateFeedbackSectionVisibility() {
    if (this.detectedClasses.length === 0) {
      this.showFeedbackSection = false;
    }
  }
}