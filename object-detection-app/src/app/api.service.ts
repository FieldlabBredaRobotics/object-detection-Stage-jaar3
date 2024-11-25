import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000'; // Je back-end URL

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

  saveProductMatch(userInput: string, detectedProduct: string, correctProduct: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/save_product_match`, { userInput, detectedProduct, correctProduct });
  }

  getProductStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_product_stats`);
  }
}
