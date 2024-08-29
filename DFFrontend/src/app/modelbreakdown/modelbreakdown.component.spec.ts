import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelbreakdownComponent } from './modelbreakdown.component';

describe('ModelbreakdownComponent', () => {
  let component: ModelbreakdownComponent;
  let fixture: ComponentFixture<ModelbreakdownComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModelbreakdownComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelbreakdownComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
