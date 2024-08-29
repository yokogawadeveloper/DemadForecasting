import { NgModule } from "@angular/core";
import { Routes, RouterModule } from "@angular/router";
import { LoginComponent } from "./login/login.component";
import { HomeComponent } from "./home/home.component";
import { DashboardComponent } from './dashboard/dashboard.component';
import { DownloadComponent } from './download/download.component';
import { UploadFilesComponent } from './upload-files/upload-files.component';
import { StaticfilesComponent } from './staticfilesUpload/staticfiles.component';
import { StaticfilesDownloadComponent } from './staticfiles-download/staticfiles-download.component';
import { ModelbreakdownComponent } from './modelbreakdown/modelbreakdown.component';
import { AuthGuard } from './_helper/auth.guard';

const routes: Routes = [
  { path: "", component: LoginComponent },
  { path: "login", component: LoginComponent },
  {
    path: "home",
    component: HomeComponent,
    children: [
      { path: "dashboard", component: DashboardComponent, },
      { path: "upload", component: UploadFilesComponent, canActivate:[AuthGuard] },
      { path: "download", component: DownloadComponent, canActivate:[AuthGuard] },
      { path: "staticfilesupload", component: StaticfilesComponent, canActivate:[AuthGuard] },
      { path: "staticfilesdownload", component: StaticfilesDownloadComponent, canActivate:[AuthGuard] },
      { path: "codebreakdown", component: ModelbreakdownComponent, canActivate:[AuthGuard] },
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
