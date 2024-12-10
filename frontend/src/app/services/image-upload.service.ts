import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root', // Ensures it's a singleton service
})
export class ImageUploadService {
  private imageSource = new BehaviorSubject<string | null>(null); // Observable for the image URL
  currentImage$ = this.imageSource.asObservable();

  setImage(imageUrl: string) {
    this.imageSource.next(imageUrl);
  }

  clearImage() {
    this.imageSource.next(null);
  }
}
