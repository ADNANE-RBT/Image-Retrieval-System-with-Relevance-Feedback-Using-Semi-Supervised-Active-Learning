import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-group-check-box',
  imports: [CommonModule],
  templateUrl: './group-check-box.component.html',
  styles: ``
})
export class GroupCheckBoxComponent {
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
