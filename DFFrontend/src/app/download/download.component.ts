import { Component, OnInit } from '@angular/core';
import { environment } from "src/environments/environment";
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: "app-download",
  templateUrl: "./download.component.html",
  styleUrls: ["./download.component.css"]
})
export class DownloadComponent implements OnInit {
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
      (window.location.href = this.url + "download/?name=" + name, httpOptions) 
    );
  }
  downloadforecastoutput() {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    return (
      (window.location.href = this.url + "forecastoutput/?name=Forcast_output", httpOptions) 
    );
  }
}
