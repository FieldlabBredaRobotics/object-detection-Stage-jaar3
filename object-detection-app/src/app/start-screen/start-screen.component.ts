// import { Component } from '@angular/core';

// @Component({
//   selector: 'app-start-screen',
//   imports: [],
//   templateUrl: './start-screen.component.html',
//   styleUrl: './start-screen.component.css'
// })
// export class StartScreenComponent {

// }
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-start-screen',
  templateUrl: './start-screen.component.html',
  styleUrls: ['./start-screen.component.css']
})
export class StartScreenComponent {
  constructor(private router: Router) {}

  startDemo() {
    // Wanneer de knop wordt ingedrukt, navigeer naar de object-detection route
    this.router.navigate(['/object-detection']);
  }
}

