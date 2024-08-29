import { Component, OnInit, OnDestroy } from "@angular/core";
import { environment } from "src/environments/environment";
import { FileUploader } from "ng2-file-upload";
import {
  FormBuilder,
  FormGroup,
  Validators,
  FormControl
} from "@angular/forms";
import { NgxSpinnerService } from "ngx-spinner";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { CustomErrorHandlerService } from "../_helper/errorHandler";
import { Router } from "@angular/router";
import { customToaster } from "../_helper/toaster";
import { ToastrService } from "ngx-toastr";
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: "app-upload-files",
  templateUrl: "./upload-files.component.html",
  styleUrls: ["./upload-files.component.css"]
})
export class UploadFilesComponent implements OnInit, OnDestroy {
  public uploader: FileUploader = new FileUploader({ isHTML5: true });
  url = environment.apiUrl;
  threshold = "";
  requiredWeek = "";
  pipelineWeek = "";
  indentrefno = "";
  private unsubscribe = new Subject();
  dates:any = [];
  // var people = new Map<string, Person>();
  constructor(
    private formBuilder: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private spinner: NgxSpinnerService,
    private toastr: ToastrService
  ) {}
  uploadForm: FormGroup;

  ngOnInit() {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    this.http
      .get<any>(this.url + "data/", httpOptions)
      .pipe(takeUntil(this.unsubscribe))
      .subscribe(
        res => {
          if(res.value == "false"){
            let myToaster = new customToaster(this.toastr);
            myToaster.showError("Please upload new");
            myToaster.showError(res.message);
            

          } else {
            this.threshold = res.threshold;
            this.requiredWeek = res.requiredWeek;
            this.pipelineWeek = res.pipelineWeek;
            this.indentrefno = res.indentrefno;
          }
        },
        err => {
          let erorHandler = new CustomErrorHandlerService(this.router);
          let myToaster = new customToaster(this.toastr);
          myToaster.showError(erorHandler.handleErrorDashboard(err));
        }
      );

    this.http
      .get<any>(this.url + "datesofinputfiles/", httpOptions)
      .pipe(takeUntil(this.unsubscribe))
      .subscribe(
        res => {
          this.dates = res;
        },
        err => {
          let erorHandler = new CustomErrorHandlerService(this.router);
          let myToaster = new customToaster(this.toastr);
          myToaster.showError(erorHandler.handleErrorDashboard(err));
        }
      );

    this.uploadForm = this.formBuilder.group({
      manufacture: new FormControl("", Validators.required),
      inventory: new FormControl("", Validators.required),
      cpaFob: new FormControl("", Validators.required),
      grList: new FormControl("", Validators.required),
      kdParts: new FormControl("", Validators.required),
      threshold: new FormControl(""),
      pipelineWeek: new FormControl(""),
      requiredWeek: new FormControl(""),
      indentrefno : new FormControl("")

    });
  }

  onSubmit() {
    const httpOptions = {
      headers: new HttpHeaders({
        Authorization: "Bearer " + sessionStorage.getItem("accessToken")
      })
    };
    this.spinner.show();
    const formData = new FormData();
    formData.append("manufacture", this.uploadForm.get("manufacture").value);
    formData.append("inventory", this.uploadForm.get("inventory").value);
    formData.append("cpaFob", this.uploadForm.get("cpaFob").value);
    formData.append("grList", this.uploadForm.get("grList").value);
    formData.append("kdParts", this.uploadForm.get("kdParts").value);
    formData.append(
      "threshold",
      (<HTMLInputElement>document.getElementById("threshold")).value
    );
    formData.append(
      "pipelineWeek",
      (<HTMLInputElement>document.getElementById("pipelineWeek")).value
    );
    // formData.append(
    //   "indentrefno",
    //   (<HTMLInputElement>document.getElementById("indentrefno")).value
    // );
    formData.append(
      "requiredWeek",
      (<HTMLInputElement>document.getElementById("requiredWeek")).value
    );

    this.http.post<any>(this.url + "data/", formData, httpOptions).subscribe(
      res => {
        let myToaster = new customToaster(this.toastr);
        if (res.value == "false"){
          myToaster.showError(res.message);
          return this.spinner.hide();
        } 
        else{
          myToaster.showSuccess("file upload Successful");
          return this.spinner.hide();
        }
      },
      err => {
        let erorHandler = new CustomErrorHandlerService(this.router);
        let myToaster = new customToaster(this.toastr);
        myToaster.showError(erorHandler.handleErrorDashboard(err));
        return this.spinner.hide();
      }
    );
  }

  OnFileSelect(event, name) {
    const file = event.target.files[0];
    this.uploadForm.get(name).setValue(file);
  }
  ngOnDestroy() {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }
}
