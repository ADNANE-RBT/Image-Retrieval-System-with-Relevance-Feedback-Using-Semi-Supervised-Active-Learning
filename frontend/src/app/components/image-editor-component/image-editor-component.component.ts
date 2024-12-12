import { Component, Input, Output, EventEmitter, OnInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-image-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './image-editor-component.component.html',
  styles: [`
    .image-editor-container {
      display: flex;
      max-width: 100%;
      gap: 20px;
    }
    .image-preview-wrapper {
      flex: 1;
      max-width: 70%;
      border: 1px solid #ccc;
    }
    .image-canvas {
      max-width: 100%;
      max-height: 500px;
    }
    .editing-controls {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .control-section {
      border: 1px solid #eee;
      padding: 15px;
      border-radius: 5px;
    }
    .crop-inputs, .resize-inputs {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
    }
    input[type="number"] {
      width: 70px;
    }
    .action-buttons {
      display: flex;
      gap: 10px;
    }
  `]
})
export class ImageEditorComponent implements OnInit {
  @ViewChild('imageCanvas', { static: true }) canvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  @Input() maxImageSize = 1000; // Max image size in pixels
  @Output() imageProcessed = new EventEmitter<Blob>();

  private ctx!: CanvasRenderingContext2D;
  private originalImage: HTMLImageElement | null = null;

  // Editing state
  rotationAngle = 0;
  cropX = 0;
  cropY = 0;
  cropWidth = 0;
  cropHeight = 0;
  resizeWidth = 0;
  resizeHeight = 0;
  maintainAspectRatio = true;

  ngOnInit() {
    const canvas = this.canvas.nativeElement;
    this.ctx = canvas.getContext('2d')!;
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          this.loadImage(img);
        };
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  loadImage(img: HTMLImageElement) {
    this.originalImage = img;
    
    // Scale down if needed
    const scaleFactor = this.maxImageSize / Math.max(img.width, img.height);
    const scaledWidth = img.width * (scaleFactor < 1 ? scaleFactor : 1);
    const scaledHeight = img.height * (scaleFactor < 1 ? scaleFactor : 1);

    const canvas = this.canvas.nativeElement;
    canvas.width = scaledWidth;
    canvas.height = scaledHeight;

    // Reset all editing parameters
    this.rotationAngle = 0;
    this.cropX = 0;
    this.cropY = 0;
    this.cropWidth = scaledWidth;
    this.cropHeight = scaledHeight;
    this.resizeWidth = scaledWidth;
    this.resizeHeight = scaledHeight;

    this.drawImage();
  }

  drawImage() {
    if (!this.originalImage) return;

    const canvas = this.canvas.nativeElement;
    const ctx = this.ctx;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Save context state
    ctx.save();

    // Move to center for rotation
    ctx.translate(canvas.width / 2, canvas.height / 2);
    
    // Rotate
    ctx.rotate(this.rotationAngle * Math.PI / 180);

    // Draw image centered
    ctx.drawImage(
      this.originalImage, 
      -canvas.width / 2, 
      -canvas.height / 2, 
      canvas.width, 
      canvas.height
    );

    // Restore context
    ctx.restore();
  }

  applyRotation() {
    this.drawImage();
  }

  applyCrop() {
    if (!this.originalImage) return;

    const canvas = this.canvas.nativeElement;
    const ctx = this.ctx;

    // Ensure crop values are within bounds
    this.cropX = Math.max(0, Math.min(this.cropX, canvas.width));
    this.cropY = Math.max(0, Math.min(this.cropY, canvas.height));
    this.cropWidth = Math.min(this.cropWidth, canvas.width - this.cropX);
    this.cropHeight = Math.min(this.cropHeight, canvas.height - this.cropY);

    // Create a new canvas for cropping
    const croppedCanvas = document.createElement('canvas');
    croppedCanvas.width = this.cropWidth;
    croppedCanvas.height = this.cropHeight;
    const croppedCtx = croppedCanvas.getContext('2d')!;

    // Draw the cropped portion
    croppedCtx.drawImage(
      canvas, 
      this.cropX, this.cropY, 
      this.cropWidth, this.cropHeight,
      0, 0, 
      this.cropWidth, this.cropHeight
    );

    // Update main canvas
    canvas.width = this.cropWidth;
    canvas.height = this.cropHeight;
    ctx.drawImage(croppedCanvas, 0, 0);

    // Update resize dimensions
    this.resizeWidth = this.cropWidth;
    this.resizeHeight = this.cropHeight;
  }

  resetCrop() {
    if (!this.originalImage) return;

    const canvas = this.canvas.nativeElement;
    this.cropX = 0;
    this.cropY = 0;
    this.cropWidth = canvas.width;
    this.cropHeight = canvas.height;

    this.loadImage(this.originalImage);
  }

  applyResize() {
    if (!this.originalImage) return;

    const canvas = this.canvas.nativeElement;
    
    // Maintain aspect ratio if checkbox is checked
    if (this.maintainAspectRatio) {
      const aspectRatio = canvas.width / canvas.height;
      
      if (this.resizeWidth) {
        this.resizeHeight = Math.round(this.resizeWidth / aspectRatio);
      } else if (this.resizeHeight) {
        this.resizeWidth = Math.round(this.resizeHeight * aspectRatio);
      }
    }

    // Create a new canvas with resized dimensions
    const resizedCanvas = document.createElement('canvas');
    resizedCanvas.width = this.resizeWidth;
    resizedCanvas.height = this.resizeHeight;
    const resizedCtx = resizedCanvas.getContext('2d')!;

    // Draw the image scaled to new size
    resizedCtx.drawImage(canvas, 0, 0, this.resizeWidth, this.resizeHeight);

    // Update main canvas
    canvas.width = this.resizeWidth;
    canvas.height = this.resizeHeight;
    this.ctx.drawImage(resizedCanvas, 0, 0);
  }

  saveImage() {
    if (!this.canvas) return;

    this.canvas.nativeElement.toBlob((blob) => {
      if (blob) {
        this.imageProcessed.emit(blob);
      }
    });
  }
}


