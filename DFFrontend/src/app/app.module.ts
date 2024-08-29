import { BrowserModule } from '@angular/platform-browser';
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

import { AppComponent } from './app.component';
import { RouterModule } from '@angular/router';
import { HttpClientModule } from "@angular/common/http";

import { FileUploadModule } from "ng2-file-upload"; 

import { ReactiveFormsModule } from "@angular/forms";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AngularMeterialModule } from './angular-meterial/angular-meterial.module';
import { NavComponent } from './nav/nav.component';
import { LoginComponent } from './login/login.component';
import { AppRoutingModule } from './app-routing.module';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DownloadComponent } from './download/download.component';
import { NgxSpinnerModule } from "ngx-spinner";
import { UploadFilesComponent } from './upload-files/upload-files.component';
import { StaticfilesComponent } from './staticfilesUpload/staticfiles.component';
import { NgxPaginationModule } from "ngx-pagination";
import { NgMaterialMultilevelMenuModule } from "ng-material-multilevel-menu";
import { StaticfilesDownloadComponent } from './staticfiles-download/staticfiles-download.component';
import { ToastrModule } from "ngx-toastr";
import { MatDialogModule, MatButtonModule } from '@angular/material';
import { ConfirmDialogComponent } from './confirm-dialog/confirm-dialog.component';
import { NgxFileDropModule } from 'ngx-file-drop';
import { ModelbreakdownComponent } from './modelbreakdown/modelbreakdown.component';
import { AuthGuard } from './_helper/auth.guard';
import { ChartsModule } from 'ng2-charts';

@NgModule({
  declarations: [
    AppComponent,
    NavComponent,
    LoginComponent,
    HomeComponent,
    DashboardComponent,
    DownloadComponent,
    UploadFilesComponent,
    StaticfilesComponent,
    StaticfilesDownloadComponent,
    ConfirmDialogComponent,
    ModelbreakdownComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AngularMeterialModule,
    AppRoutingModule,
    RouterModule,
    HttpClientModule,
    ReactiveFormsModule,
    FileUploadModule,
    NgxSpinnerModule,
    NgMaterialMultilevelMenuModule,
    NgxPaginationModule,
    MatDialogModule,
    NgxFileDropModule,
    MatButtonModule,
    ToastrModule.forRoot({
      preventDuplicates: true,
      disableTimeOut: true,
      newestOnTop: true,
      closeButton: true,
      countDuplicates: true,
    }),
    ChartsModule
  ],
  providers: [AuthGuard],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  entryComponents: [ConfirmDialogComponent]
})
export class AppModule {}
