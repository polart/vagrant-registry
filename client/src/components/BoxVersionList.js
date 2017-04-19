import React, {Component} from "react";
import {connect} from "react-redux";
import {Label, Pagination, Panel} from "react-bootstrap";
import ReactMarkdown from "react-markdown";
import Moment from "moment";
import * as actions from "../actions";
import MySpinner from "./MySpinner";
import {Link} from "react-router";


class BoxVersionList extends Component {
  state = {
    page: 1,
  };

  componentDidMount() {
    this.props.fetchBoxVersions(this.props.boxTag, this.state.page);
  }

  onPageChange = (page) => {
    this.props.fetchBoxVersions(this.props.boxTag, page);
    this.setState({page});
  };

  renderPagination = () => {
    if (this.pages.count <= 10) {
      return null;
    }

    const items = Math.ceil(this.pages.count / 10);
    return (
        <div className="text-center">
          <Pagination
              prev
              next
              first
              last
              ellipsis
              boundaryLinks
              items={items}
              maxButtons={5}
              activePage={this.state.page}
              onSelect={this.onPageChange}
          />
        </div>
    );
  };

  renderProviders = (version) => {
    return version.providers.map((providerTag) => {
      const provider = this.props.boxProviders[providerTag];
      return (
          <span key={providerTag} >
            <Label bsStyle="primary">
              {provider.provider}
            </Label>
            &nbsp;
          </span>
      );
    });
  };

  renderVersionsList = () => {
    return this.versionTags.map(tag => {
      const version = this.props.boxVersions[tag];
      return (
          <Link
              to={`/boxes/${this.props.boxTag}/versions/${version.version}/`}
              key={version.version}
          >
            <Panel>
              <h4 className="list-group-item-heading">
                v{version.version}
                {' '}
                <small title={Moment(version.date_updated).format('LLL')}>
                  | Last updated: {Moment(version.date_updated).fromNow()}
                </small>
              </h4>
              <ReactMarkdown source={version.changes} />
              {this.renderProviders(version)}
            </Panel>
          </Link>
      );
    });
  };

  render() {
    this.pages = this.props.boxVersionsPages;
    this.versionTags = (this.pages && this.pages.pages[this.state.page]) || [];

    if (!this.pages || !this.versionTags.length) {
      return <MySpinner />;
    }

    if (this.pages.count === 0) {
      return <p>No versions</p>
    }

    return (
        <div>
          <div className="box-list">
            {this.renderVersionsList()}
          </div>
          {this.renderPagination()}
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    boxVersions: state.entities.boxVersions,
    boxVersionsPages: state.pagination.boxVersions[props.boxTag],
    boxProviders: state.entities.boxProviders,
  };
}

export default connect(mapStateToProps, {
  fetchBoxVersions: actions.loadBoxVersions,
})(BoxVersionList)
