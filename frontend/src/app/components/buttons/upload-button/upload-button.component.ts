import { Component, ElementRef, ViewChild, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImageUploadService } from '../../../services/image-upload.service';


@Component({
  selector: 'app-upload-button',
  imports: [CommonModule], 
  templateUrl: './upload-button.component.html',
  styles:''
})
export class UploadbuttonComponent {
  constructor(private imageUploadService: ImageUploadService) {}

  previewUrl: string | null = null;
  fileName: string | null = null;
  
  @Input() version!: number; // Define the input property
  @ViewChild('fileInput') fileInputRef!: ElementRef<HTMLInputElement>;

  handleButtonClick(): void {
    this.fileInputRef.nativeElement.click();
  }

  handleFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      this.fileName = file.name;
      const reader = new FileReader();
      reader.onload = () => {
        this.imageUploadService.setImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }

  handleRemove(): void {
    this.previewUrl = null;
    this.fileName = null;
    if (this.fileInputRef) {
      this.fileInputRef.nativeElement.value = '';
    }
  }
}
