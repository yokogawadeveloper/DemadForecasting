import { Component, OnInit } from '@angular/core';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";
import { NgxSpinnerService } from 'ngx-spinner';
import { customToaster } from '../_helper/toaster';
import { ToastrService } from 'ngx-toastr';
import { CustomErrorHandlerService } from '../_helper/errorHandler';
import { Router } from '@angular/router';

@Component({
  selector: 'app-modelbreakdown',
  templateUrl: './modelbreakdown.component.html',
  styleUrls: ['./modelbreakdown.component.css']
})
export class ModelbreakdownComponent implements OnInit {
  showTable=false;

  ngOnInit() {
  }
  url = environment.apiUrl;
  constructor(
    private httpService: HttpClient,
    private spinner: NgxSpinnerService,
    private toastr: ToastrService,
    private router: Router,
  ) { }

  public files: NgxFileDropEntry[] = [];
 
  public dropped(files: NgxFileDropEntry[]) {
    this.showTable=true
    this.files = files;
    for (const droppedFile of files) {
      // Is it a file?
      if (droppedFile.fileEntry.isFile) {
        this.spinner.show();
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        fileEntry.file((file: File) => {
          // You could upload it like this:
          const formData = new FormData()
          formData.append('modelFile', file, droppedFile.relativePath)
 
          // Headers
          const httpOptions = {
            headers: new HttpHeaders({
              Authorization: "Bearer " + sessionStorage.getItem("accessToken"),
            })
          };
          this.httpService.post(this.url + "modeltoparts/", formData, httpOptions)
          .subscribe(
            res => {
            let myToaster = new customToaster(this.toastr);
            myToaster.showSuccess(res['message']);
            this.spinner.hide();
          },
          err => {
            let erorHandler = new CustomErrorHandlerService(this.router);
            let myToaster = new customToaster(this.toastr);
            myToaster.showError(erorHandler.handleErrorDashboard(err));
            this.spinner.hide();
          })           
        });
      } 
    }
  }
  downloadFile(){
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    return (
      (window.location.href = this.url + "download/?name=listOfQty", httpOptions) 
    );
  }
}
