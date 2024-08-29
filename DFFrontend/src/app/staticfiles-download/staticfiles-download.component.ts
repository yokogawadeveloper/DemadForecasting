import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: "app-staticfiles-download",
  templateUrl: "./staticfiles-download.component.html",
  styleUrls: ["./staticfiles-download.component.css"]
})
export class StaticfilesDownloadComponent implements OnInit {
  url = environment.apiUrl;
  constructor() {}

  ngOnInit() {}
  downloadFile(name: any) {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    return (
      (window.location.href = this.url + "staticfilesdownload/?name=" + name),
      httpOptions
    );
  }
}
