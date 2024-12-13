import { Component } from '@angular/core';
import { ImageCardComponent } from '../../components/image-card-component/image-card-component.component';
import { CommonModule } from '@angular/common';
import { GroupCheckBoxComponent } from '../../components/group-check-box/group-check-box.component';

@Component({
  selector: 'app-home-page',
  imports: [ImageCardComponent, CommonModule, GroupCheckBoxComponent],
  templateUrl: './home-page.component.html',
  styles: ``
})
export class HomePageComponent {
  checkboxGroups = [
    { id: 'checkbox-08-1', label: 'React' },
    { id: 'checkbox-08-2', label: 'Next.js' },
    { id: 'checkbox-08-3', label: 'Astro' },
    { id: 'checkbox-08-4', label: 'Angular' },
    { id: 'checkbox-08-5', label: 'Vue' },
    { id: 'checkbox-08-6', label: 'Svelte' },
    { id: 'checkbox-08-7', label: 'SolidJS' },
  ];
}
