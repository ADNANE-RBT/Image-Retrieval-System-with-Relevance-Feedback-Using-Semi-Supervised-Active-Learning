import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ImageUploadService {
  private imageSource = new BehaviorSubject<string | null>(null);
  private fileSource = new BehaviorSubject<File | null>(null); 

  currentImage$ = this.imageSource.asObservable();
  uploadedFile$ = this.fileSource.asObservable();

  setImage(imageUrl: string) {
    this.imageSource.next(imageUrl);
  }

  setFile(file: File) {
    this.fileSource.next(file); 
  }

  clearImage() {
    this.imageSource.next(null); 
    this.fileSource.next(null); 
  }
}
