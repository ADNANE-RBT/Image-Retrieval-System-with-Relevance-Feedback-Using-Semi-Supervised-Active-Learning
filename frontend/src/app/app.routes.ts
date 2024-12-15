import { Routes } from '@angular/router';
import { LandingPageComponent } from './layouts/landing-page/landing-page.component';
import { MainPageComponent } from './layouts/main-page/main-page.component';
import { LandingPageContentComponent } from './pages/landing-page-content/landing-page-content.component';
import { UploadpageComponent } from './pages/main-page-content/upload-page.component';
import { EditPageComponent } from './pages/edit-page/edit-page.component';
import { SearchPageComponent } from './pages/search-page/search-page.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { ImageViewComponent } from './pages/image-view/image-view.component';
import { ImageEditorComponent } from './components/image-editor-component/image-editor-component.component';

export const routes: Routes = [
  {
    path: '',
    component: LandingPageComponent,
    children: [
      { path: '', component: LandingPageContentComponent },
    ],
  },
  {
    path: 'home',
    component: MainPageComponent,
    children: [
      { path: '', component: HomePageComponent },
      // { path: 'image', component: ImageViewComponent },
      { path: 'image/:id', component: ImageViewComponent }

    ],
  },
  {
    path: 'upload',
    component: MainPageComponent, 
    children: [
      { path: '', component: UploadpageComponent },
    ],
  },{
    path: 'edit',
    component: MainPageComponent,
    children: [
      // { path: 'image/:id', component: ImageEditComponent },
      { path: 'images/:id', component: ImageEditorComponent },
      { path: '', component: EditPageComponent },
    ],
  },
  {
    path: 'search',
    component: MainPageComponent,
    children: [
      { path: '', component: SearchPageComponent },
    ],
  },
];
