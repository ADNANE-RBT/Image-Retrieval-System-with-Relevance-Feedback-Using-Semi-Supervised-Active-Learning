import { Routes } from '@angular/router';
import { LandingPageComponent } from './layouts/landing-page/landing-page.component';
import { MainPageComponent } from './layouts/main-page/main-page.component';
import { LandingPageContentComponent } from './pages/landing-page-content/landing-page-content.component';
import { MainPageContentComponent } from './pages/main-page-content/main-page-content.component';

export const routes: Routes = [
  {
    path: '',
    component: LandingPageComponent,
    children: [
      { path: '', component: LandingPageContentComponent },
    ],
  },
  {
    path: 'main',
    component: MainPageComponent,
    children: [
      { path: '', component: MainPageContentComponent },
    ],
  },
];
