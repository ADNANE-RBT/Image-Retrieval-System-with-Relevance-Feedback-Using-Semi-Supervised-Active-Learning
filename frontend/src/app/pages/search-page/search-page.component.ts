import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface SemiSupervisedSearchResult {
  similar_images: string[];
  search_type?: string;
  feedback_applied?: boolean;
}
interface SimilarImage {
  image_path: string;
  similarity_score: number;
}

interface SimpleSearchResult {
  search_type: string;
  similar_images: SimilarImage[];
}


@Component({
  selector: 'app-search-page',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule],
  templateUrl: './search-page.component.html',
  styles: [`
    .feedback-section button {
      display: block;
      margin: 5px 0;
    }
    .image-container {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .image-item {
      position: relative;
      cursor: pointer;
    }
    .image-item.relevant {
      border: 2px solid green;
    }
    .image-item.non-relevant {
      border: 2px solid red;
    }
  `]
})
export class SearchPageComponent {
  selectedFile: File | null = null;
  similarImages: string[] = [];
  searchMode: 'simple' | 'semi-supervised' | null = null;
  relevantImages: string[] = [];
  nonRelevantImages: string[] = [];
  isLoading: boolean = false;
  constructor(private http: HttpClient) {}


  uploadedImage: string | null = null; // To store the image data URL
  uploadedLabel: string | null = null; // To store the label for the uploaded image

  onFileSelected(event: Event): void {
    const fileInput = event.target as HTMLInputElement;
    if (fileInput.files && fileInput.files[0]) {
      
      const file = fileInput.files[0];

      this.uploadedLabel = file.name; // Set the label to the file name
      this.selectedFile = file;
      this.similarImages = [];
      this.searchMode = null;
      this.relevantImages = [];
      this.nonRelevantImages = [];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.uploadedImage = e.target?.result as string; // Set the image data URL
      };
      reader.readAsDataURL(file);
    }
  }

  performSimpleSearch() {
    if (!this.selectedFile) return;
    this.isLoading = true;
    const formData = new FormData();
    formData.append('image', this.selectedFile);
    formData.append('top_k', '10');
  
    this.http.post<SimpleSearchResult>('http://localhost:5000/simple_search', formData)
      .subscribe({
        next: (response) => {
          console.log('API Response:', response); // Debugging purposes
          if (response.similar_images && Array.isArray(response.similar_images)) {
            // Extract only image paths
            this.similarImages = response.similar_images.map(item => item.image_path);
            this.searchMode = 'simple';
            this.isLoading = false;
          } else {
            console.error('Unexpected response structure', response);
            this.isLoading = false;
          }
        },
        error: (error) => {
          console.error('Simple search failed', error);
          alert('Image search failed');
          this.isLoading = false;
        }
      });
  }
  
  

  performSemiSupervisedSearch() {
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('image', this.selectedFile);
    this.isLoading = true;
    this.http.post<SemiSupervisedSearchResult>('http://localhost:5000/semi_supervised_search', formData)
      .subscribe({
        next: (response) => {
          this.similarImages = response.similar_images.map(str => str.replace(/\\/g, "/").replace("../../Dataset/RSSCN7-master/",""));
          this.searchMode = 'semi-supervised';
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Semi-supervised search failed', error);
          alert('Semi-supervised image search failed');
          this.isLoading = false;
        }
      });
  }

  toggleRelevance(image: string) {
    const relevantIndex = this.relevantImages.indexOf(image);
    const nonRelevantIndex = this.nonRelevantImages.indexOf(image);

    if (relevantIndex > -1) {
      this.relevantImages.splice(relevantIndex, 1);
      this.nonRelevantImages.push(image);
    } else if (nonRelevantIndex > -1) {
      this.nonRelevantImages.splice(nonRelevantIndex, 1);
    } else {
      this.relevantImages.push(image);
    }
  }

  refineSearch() {
    if (!this.selectedFile) return;
  
    const formData = new FormData();
    formData.append('image', this.selectedFile);
  
    // Modify image paths to include full dataset path and convert forward slashes to backslashes
    const feedback = {
      relevant: this.relevantImages.map(img => `../../Dataset/RSSCN7-master\\${img.replace(/\//g, '\\')}`),
      non_relevant: this.nonRelevantImages.map(img => `../../Dataset/RSSCN7-master\\${img.replace(/\//g, '\\')}`)
    };
  
    console.log('Sending feedback:', feedback);
    console.log('Feedback as JSON string:', JSON.stringify(feedback));
  
    formData.append('feedback', JSON.stringify(feedback));
  
    this.http.post<SemiSupervisedSearchResult>('http://localhost:5000/semi_supervised_search', formData)
      .subscribe({
        next: (response) => {
          console.log('Refinement response:', response);
          if (response.similar_images) {
            this.similarImages = response.similar_images.map(str => 
              str.replace(/\\/g, "/").replace("../../Dataset/RSSCN7-master/","")
            );
            this.relevantImages = [];
            this.nonRelevantImages = [];
          } else {
            console.error('No similar images in response');
          }
        },
        error: (error) => {
          console.error('Refinement failed', error);
          console.error('Error details:', error.error);
          alert('Search refinement failed');
        }
      });
  }
  


  isRelevant(image: string): boolean {
    return this.relevantImages.includes(image);
  }

  isNonRelevant(image: string): boolean {
    return this.nonRelevantImages.includes(image);
  }
}