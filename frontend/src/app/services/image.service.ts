import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interface for Image model
export interface ImageDimensions {
  width: number;
  height: number;
}

export interface Image {
  _id?: string;
  filename: string;
  path: string;
  size: number;
  category: string;
  dimensions: ImageDimensions;
  createdAt?: Date;
  updatedAt?: Date;
}

@Injectable({
  providedIn: 'root'
})
export class ImageService {
  private apiUrl = 'http://localhost:5000/api/images';

  constructor(private http: HttpClient) {}

  // Upload a new image
  uploadImage(image: File, category: string): Observable<Image> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('category', category);

    return this.http.post<Image>(`${this.apiUrl}/upload`, formData);
  }

  // Fetch all images
  getAllImages(): Observable<Image[]> {
    return this.http.get<Image[]>(this.apiUrl);
  }

  // Fetch images by category 
  getImagesByCategory(categories: string | string[]): Observable<Image[]> {
    // Convert single category to array if needed
    const categoryParam = Array.isArray(categories) 
      ? categories.join(',') 
      : categories;

    return this.http.get<Image[]>(`${this.apiUrl}/category`, {
      params: { categories: categoryParam }
    });
  }

  // Get a single image by ID
  getImageById(id: string): Observable<Image> {
    return this.http.get<Image>(`${this.apiUrl}/${id}`);
  }

  // Delete an image by ID
  deleteImage(id: string): Observable<{ message: string, image: Image }> {
    return this.http.delete<{ message: string, image: Image }>(`${this.apiUrl}/${id}`);
  }

  // Update image metadata
  updateImage(
    id: string, 
    updateData: { category?: string, filename?: string }
  ): Observable<{ message: string, image: Image }> {
    return this.http.patch<{ message: string, image: Image }>(
      `${this.apiUrl}/${id}`, 
      updateData
    );
  }
}