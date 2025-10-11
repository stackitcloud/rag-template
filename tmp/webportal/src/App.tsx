import { Component } from 'solid-js';
import { Router, Route } from '@solidjs/router';
import Home from './components/Home';
import Address from './components/Address';
import Result from './components/Result';

const App: Component = () => {
	return (
		<Router>
			<Route path="/" component={Home} />
			<Route path="/address" component={Address} />
			<Route path="/result" component={Result} />
		</Router>
	);
};

export default App;