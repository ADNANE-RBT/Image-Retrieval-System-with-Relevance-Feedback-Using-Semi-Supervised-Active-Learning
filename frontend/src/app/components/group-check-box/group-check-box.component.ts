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
    { id: 'checkbox-08-1', label: 'aGrass' },
    { id: 'checkbox-08-2', label: 'bField' },
    { id: 'checkbox-08-3', label: 'cIndustry' },
    { id: 'checkbox-08-4', label: 'dRiverLake' },
    { id: 'checkbox-08-5', label: 'eForest' },
    { id: 'checkbox-08-6', label: 'fResident' },
    { id: 'checkbox-08-7', label: 'gParking' },
  ];
}
