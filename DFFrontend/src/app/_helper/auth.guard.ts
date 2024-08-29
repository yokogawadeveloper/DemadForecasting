import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';
import { Router } from '@angular/router';

@Injectable()
export class AuthGuard implements CanActivate {
    canActivate() {
        if (sessionStorage.getItem("role") == 'admin') {
            return true;
        }
        return false;
    }

    constructor(private router: Router) { }
}
