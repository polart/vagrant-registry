import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual} from "lodash";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";
import {BOX_ORDERING, DEFAULT_BOX_ORDERING} from "../constants";
import BoxList from "./BoxList";


class BoxListPage extends Component {
  componentDidMount() {
    this.fetchBoxes();
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.location.query, this.props.location.query)) {
      // For a case, when changing page or ordering.
      this.fetchBoxes();
      return;
    }

    if (prevProps.params.username !== this.props.params.username) {
      // For a case, when navigating by breadcrumb,
      // or back and forth in browser.
      this.fetchBoxes();
    }
  }

  fetchBoxes = () => {
    this.props.fetchBoxes(
        this.props.params.username,
        this.props.location.query.page || 1,
        BOX_ORDERING[this.props.location.query.order] || DEFAULT_BOX_ORDERING,
        this.props.location.query.q
    );
  };

  render() {
    this.username = this.props.params.username;
    let pageTitle = 'All boxes';
    if (this.username) {
      pageTitle = `${this.username}'s boxes`
    }
    return (
        <div>
          <PageHeader>{pageTitle}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          <BoxList
              router={this.props.router}
              boxes={this.props.boxes}
              boxesPages={this.props.boxesPages}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    boxes: state.entities.boxes,
    boxesPages: state.pagination.boxes[
        props.params.username || '__all__'
    ],
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(BoxListPage)
