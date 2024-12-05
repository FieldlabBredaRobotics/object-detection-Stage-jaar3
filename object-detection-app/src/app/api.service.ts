import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000'; //back-end URL

  constructor(private http: HttpClient) {}

  startDetection(): Observable<any> {
    return this.http.get(`${this.apiUrl}/start_detection`);
  }

  stopDetection(): Observable<any> {
    return this.http.get(`${this.apiUrl}/stop_detection`);
  }

  processNaturalLanguage(text: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/process_natural_language`, { text });
  }

  saveProductMatch(detectedProduct: string, correctProduct: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/save_product_match`, { detectedProduct, correctProduct });
  }

  saveTextMatch(detectedProduct: string, correctProduct: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/save_text_match`, { detectedProduct, correctProduct });
  }

  getProductStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_product_stats`);
  }

  captureAndDetect(): Observable<any> {
    return this.http.post(`${this.apiUrl}/capture_and_detect`, {});
  }

  setTarget(objectName: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/set_target/${objectName}`, {});
  }

  getDetectionStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_detection_status`);
  }
  getObjectDetectionStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_object_detection_stats`);
  }
  
  getProductDetectionAccuracy(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_product_detection_accuracy`);
  }
  
  getTextDetectionAccuracy(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_text_detection_accuracy`);
  }
}	